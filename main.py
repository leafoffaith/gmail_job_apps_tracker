import os
import re
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import sheets_upload
import auto_apply

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send', 
    'https://www.googleapis.com/auth/spreadsheets'
]

CSV_FILE = 'job_applications.csv'


def authenticate_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service


def search_sent_emails(service, query):
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return messages


def get_subject_and_date(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['Subject']).execute()
    headers = msg['payload']['headers']
    subject = None
    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value']
            break
    # Get internalDate (milliseconds since epoch)
    internal_date = msg.get('internalDate')
    if internal_date:
        from datetime import datetime
        date_str = datetime.utcfromtimestamp(int(internal_date) / 1000).strftime('%Y-%m-%d %H:%M:%S')
    else:
        date_str = ''
    return subject, date_str


def extract_company(subject):
    match = re.search(r'Re: Data Engineering at (.+)', subject, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ''


def append_to_csv(subject, company, date_sent):
    status = 'in progress'
    # If file doesn't exist, create and write
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame([[subject, company, date_sent, status]], columns=['Subject', 'Company', 'Date', 'Status'])
        df.to_csv(CSV_FILE, index=False)
        return
    # Read existing companies
    df = pd.read_csv(CSV_FILE)
    existing_companies = df['Company'].astype(str).str.strip().str.lower().tolist()
    if company.strip().lower() in existing_companies:
        print(f"Company '{company}' already exists. Skipping.")
        return
    # Append new entry
    new_df = pd.DataFrame([[subject, company, date_sent, status]], columns=['Subject', 'Company', 'Date', 'Status'])
    new_df.to_csv(CSV_FILE, mode='a', header=False, index=False)


def main():
    service = authenticate_gmail()
    query = 'in:sent re:data engineering'
    messages = search_sent_emails(service, query)
    if not messages:
        print('No messages found.')
        return
    for msg in messages:
        subject, date_sent = get_subject_and_date(service, msg['id'])
        if subject:
            company = extract_company(subject)
            append_to_csv(subject, company, date_sent)
            print(f'Appended: {subject} | {company} | {date_sent} | in progress')


if __name__ == '__main__':
    # main()
    # sheets_upload.upload_csv_to_sheet()
    auto_apply.main()

