import os
import pandas as pd
import pickle
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Google Sheets API scope for read/write
SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# The ID of your Google Sheet
load_dotenv()
# The range to update (entire first sheet)
SPREADSHEET_ID = os.getenv('SHEET_ID')
RANGE_NAME = 'Sheet1'  # Change if your sheet/tab is named differently
CSV_FILE = 'job_applications.csv'


def authenticate_sheets():
    """
    Authenticates and returns a Google Sheets API service instance.
    Requires credentials.json in the current directory.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SHEETS_SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('sheets', 'v4', credentials=creds)
    return service


def upload_csv_to_sheet():
    """
    Reads job_applications.csv and uploads its contents to the specified Google Sheet.
    Overwrites all data in the first sheet.
    """
    # Read CSV
    df = pd.read_csv(CSV_FILE)
    # Prepare data as list of lists (including header)
    values = [df.columns.tolist()] + df.values.tolist()

    service = authenticate_sheets()
    sheet = service.spreadsheets()
    # Clear the sheet first (optional, but ensures no leftover rows)
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    # Upload new data
    body = {'values': values}
    result = sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated in Google Sheet.")


if __name__ == '__main__':
    upload_csv_to_sheet()
