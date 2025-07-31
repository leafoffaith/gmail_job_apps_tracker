#!/usr/bin/env python3
"""
Cold Email Sender using Gmail API

Usage:
    python auto_apply.py "Company Name" "recipient@example.com"

This script sends a standardized cold email with your CV attachment.
The email template is pre-written and includes your contact information.
"""

import os
import sys
import base64
import pickle
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


def main():
    """Main function to send cold email."""
    if len(sys.argv) != 3:
        print("Usage: python auto_apply.py \"Company Name\" \"recipient@example.com\"")
        print("Example: python auto_apply.py \"TechCorp Inc\" \"john.doe@techcorp.com\"")
        sys.exit(1)
    
    company_name = sys.argv[1]
    recipient_email = sys.argv[2]
    
    # Validate email format (basic validation)
    if '@' not in recipient_email or '.' not in recipient_email:
        print("Error: Invalid email address format")
        sys.exit(1)
    
    print(f"Preparing to send cold email to {recipient_email} at {company_name}")
    
    # Get email content (fixed template)
    email_body = get_email_content(company_name)
    
    # Create subject line
    subject = f"Cold Outreach - {company_name}"
    
    # Check for CV attachment
    cv_path = "shaurya_dey_cv.pdf"
    if not os.path.exists(cv_path):
        print(f"⚠️  Warning: CV file '{cv_path}' not found. Email will be sent without attachment.")
        cv_path = None
    else:
        print(f"✅ CV attachment found: {cv_path}")
    
    # Confirm before sending
    print("\n" + "="*50)
    print("EMAIL PREVIEW")
    print("="*50)
    print(f"To: {recipient_email}")
    print(f"Subject: {subject}")
    print(f"Company: {company_name}")
    if cv_path:
        print(f"Attachment: {cv_path}")
    print("-" * 50)
    print("Content:")
    print(email_body)
    print("="*50)
    
    confirm = input("\nDo you want to send this email? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("Email cancelled.")
        sys.exit(0)
    
    # Authenticate and send
    try:
        service = authenticate_gmail()
        message = create_message(recipient_email, subject, email_body, cv_path)
        
        print("\nSending email...")
        result = send_email(service, message)
        
        if result:
            print(f"✅ Email sent successfully!")
            print(f"Message ID: {result['id']}")
            print(f"Sent to: {recipient_email}")
            print(f"Company: {company_name}")
            if cv_path:
                print(f"With attachment: {cv_path}")
        else:
            print("❌ Failed to send email")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 