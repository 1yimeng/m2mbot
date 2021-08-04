from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '11GACCkrq9fz3IxDdtEbX1S2CYyFdJv4Vxk7o89T8kFA'
SAMPLE_RANGE_NAME = 'Tracker!A1:U52'

def update_sheet(full_name, week_num, project_type):
    """Shows basic usage of the Sheets API.
    Return: -1 for no data found
            1 for already logged
            0 for failed attempt
            2 for success
            -2 for no name found
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return -1
    
    index = 0
    for name in values:
        if name[0] == full_name:
            if project_type == 'Design':
                index = int(week_num) * 2
            else:
                index = int(week_num) * 2 - 1
            if name[index] == 'TRUE':
                return 1
            name[index] = 'TRUE'

    if index == 0:
        return -2

    value_input_option = 'USER_ENTERED'
    body = {
        'values': values
    }
    # print(values)
    result = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
        valueInputOption=value_input_option, body=body).execute()
    # print('{0} cells updated.'.format(result.get('updatedCells')))
    
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    for name in values:
        if name[0] == full_name:
            if name[index] != 'TRUE':
                return 0
            return 2

    