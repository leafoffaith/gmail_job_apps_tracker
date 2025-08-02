#!/usr/bin/env python3
"""
Cold Email Automation Tool using Gmail API

Usage:
    python auto_apply.py

This script reads from email_corpus.csv and sends standardized cold emails 
to all contacts with your CV attachment. The email template is pre-written 
and includes your contact information.

CSV Format:
    Company Name,Email Address
    Company A,email1@companya.com
    Company B,email2@companyb.com
"""

import os
import sys
import base64
import pickle
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these SCOPES, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',  # Added send permission
    'https://www.googleapis.com/auth/spreadsheets'
]


def authenticate_gmail():
    """Authenticate with Gmail API using OAuth2."""
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


def create_message(to_email, subject, body, attachment_path=None):
    """Create a Gmail message with optional attachment."""
    if attachment_path and os.path.exists(attachment_path):
        # Create multipart message for attachment
        message = MIMEMultipart()
        message['to'] = to_email
        message['subject'] = subject
        
        # Add body
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)
        
        # Add attachment
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(attachment_path)}'
        )
        message.attach(part)
    else:
        # Simple text message without attachment
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


def send_email(service, message):
    """Send an email using Gmail API."""
    try:
        sent_message = service.users().messages().send(userId='me', body=message).execute()
        return sent_message
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_email_content(company_name):
    """Get the standard cold email template with company name."""
    return f"""Hi, 

Hope you are well! My name is Shaurya. I am excited by {company_name}'s work and am reaching out to apply for a data engineering position. I have 2 years of relevant experience building full-stack applications, and working with data is one of my strongest suits. I like to work across the stack, from building scalable, robust backend systems to high-throughput data ingestion pipelines to production-grade frontend components in React. 
Some of my recent projects include building end-to-end systems integrating Next.js UIs with Python- and Node-based services; an algorithmically enforced spaced repetition language learning app; and, most recently, implementing ETL pipelines and generating dashboards for Hakuhodo's data-driven integrated marketing team.

Attaching my CV for your perusal. Happy to get on a call to discuss further.
Looking forward to hearing from you! 


Warm regards

Shaurya Dey 
9811899772 
https://shaurya-showcase-portfolio.vercel.app/"""


def read_email_corpus():
    """Read the email corpus CSV file."""
    csv_file = 'email_corpus.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return None
    
    try:
        df = pd.read_csv(csv_file)
        if 'Company Name' not in df.columns or 'Email Address' not in df.columns:
            print("Error: CSV must have 'Company Name' and 'Email Address' columns")
            return None
        return df
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return None


def send_single_email(service, company_name, recipient_email, cv_path):
    """Send a single email to one recipient."""
    email_body = get_email_content(company_name)
    subject = f"Re: Data Engineering at {company_name}"
    
    try:
        message = create_message(recipient_email, subject, email_body, cv_path)
        result = send_email(service, message)
        
        if result:
            print(f"✅ Sent to {recipient_email} at {company_name}")
            return True
        else:
            print(f"❌ Failed to send to {recipient_email} at {company_name}")
            return False
    except Exception as e:
        print(f"❌ Error sending to {recipient_email} at {company_name}: {e}")
        return False


def main():
    """Main function to send cold emails to all contacts in email_corpus.csv."""
    print("🚀 Cold Email Automation Tool")
    print("="*50)
    
    # Read email corpus
    df = read_email_corpus()
    if df is None:
        sys.exit(1)
    
    print(f"📧 Found {len(df)} contacts in email_corpus.csv")
    
    # Check for CV attachment
    cv_path = "shaurya_dey_cv.pdf"
    if not os.path.exists(cv_path):
        print(f"⚠️  Warning: CV file '{cv_path}' not found. Emails will not be sent without attachment.")
        cv_path = None
        sys.exit(1)
    else:
        print(f"✅ CV attachment found: {cv_path}")
    
    # Show preview of all emails
    print("\n" + "="*50)
    print("EMAIL PREVIEW")
    print("="*50)
    for index, row in df.iterrows():
        company_name = row['Company Name']
        email = row['Email Address']
        subject = f"Re: Data Engineering at {company_name}"
        print(f"{index + 1}. {email} at {company_name}")
        print(f"   Subject: {subject}")
    
    print("="*50)
    print(f"Total emails to send: {len(df)}")
    if cv_path:
        print(f"With attachment: {cv_path}")
    
    # Confirm before sending
    confirm = input("\nDo you want to send all these emails? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("Email sending cancelled.")
        sys.exit(0)
    
    # Authenticate Gmail
    try:
        service = authenticate_gmail()
        print("\n✅ Gmail authentication successful")
    except Exception as e:
        print(f"❌ Gmail authentication failed: {e}")
        sys.exit(1)
    
    # Send emails
    print("\n📤 Sending emails...")
    print("-" * 50)
    
    successful = 0
    failed = 0
    
    for index, row in df.iterrows():
        company_name = row['Company Name']
        email = row['Email Address']
        
        print(f"\n[{index + 1}/{len(df)}] Sending to {email} at {company_name}...")
        
        if send_single_email(service, company_name, email, cv_path):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*50)
    print("SENDING SUMMARY")
    print("="*50)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📧 Total: {len(df)}")
    print("="*50)
    
    if successful > 0:
        print("🎉 Cold email campaign completed!")
    else:
        print("😞 No emails were sent successfully.")


if __name__ == '__main__':
    main() 