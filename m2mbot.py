import logging
import json
import os
import requests
from slack_bolt import App, Say, Ack
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, jsonify, make_response, abort
from googleedit import update_sheet
from slack_sdk import WebClient
from dotenv import load_dotenv

##### Change hardcoded channel
load_dotenv()
token = os.getenv("SLACK_BOT_TOKEN")
signing_secret = os.getenv("SLACK_SIGNING_SECRET")
# Initializes your app with your bot token and signing secret
app = App(
    token=token,
    signing_secret=signing_secret)

client = WebClient(token)
@app.command("/project")
def handle_command(body, ack, respond, client, logger):
    logger.info(body)
    # print(body)
    # global channel_id
    # channel_id = body['channel_id']
    ack(
        text="Accepted!",
        blocks=[
            {
                "type": "section",
                "block_id": "b",
                "text": {"type": "mrkdwn", "text": ":white_check_mark: Accepted!",},
            }
        ],
    )

    res = client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "view-id",
            "title": {
                "type": "plain_text",
                "text": "Project Submission",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "input",
                    "block_id": "firstblock",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Full Name",
                        "emoji": False
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "input",
                    "block_id": "secondblock",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Week #",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "block_id": "thirdblock",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Type of project"
                    },
                    "accessory": {
                        "type": "static_select",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Select an item",
                            "emoji": True
                        },
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Design",
                                    "emoji": True
                                },
                                "value": "value-0"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Coding",
                                    "emoji": True
                                },
                                "value": "value-1"
                            }
                        ],
                        "action_id": "static_select-action"
                    }
                }
            ]
        }
    )
    logger.info(res)

@app.view("view-id")
def handle_view_events(ack, body, logger):
    ack()
    logger.info(body)
    full_name = body['view']['state']['values']['firstblock']['plain_text_input-action']['value']
    week_num = body['view']['state']['values']['secondblock']['plain_text_input-action']['value']
    project_type = body['view']['state']['values']['thirdblock']['static_select-action']['selected_option']['text']['text']
    try:
        result = update_sheet(full_name, week_num, project_type)
        channel_id = 'C029BUBH5T2'
        if result == 1:
            client.chat_postMessage(channel=channel_id, text= f'Hi {full_name}, the {project_type} project at week {week_num} is already logged.')
        elif result == -1:
            client.chat_postMessage(channel=channel_id, text= 'Hi ' + full_name + ', the spreadsheet is not found.')
        elif result == 0:
            client.chat_postMessage(channel=channel_id, text= 'Hi ' + full_name + ', the attempt is failed.')
        elif result == 2:
            client.chat_postMessage(channel=channel_id, text= f'Hi {full_name}, the {project_type} project at week {week_num} is successfully logged.')
        elif result == -2:
            client.chat_postMessage(channel=channel_id, text= 'Hi ' + full_name + ', please re-try the command, your name is not found in the spread sheet.')
    except:
        channel_id = 'C029BUBH5T2'
        client.chat_postMessage(channel=channel_id, text= 'ERROR IN LOGGING, contact Yi Meng Wang with this issue')

@app.action("static_select-action")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)
    # print(body)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/projectsubmit", methods=["POST"])
def open_sesame():
    data = request.get_data()
    handler.handle(request)
    # print(data)
    return ("", 200)

@flask_app.route("/interactive-endpoint", methods=["POST"])
def interactive_endpoint():
    data = request.get_data()
    handler.handle(request)
    # print(data)
    return ("", 200)

# Start your app
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=3000)