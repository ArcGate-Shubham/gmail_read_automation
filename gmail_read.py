import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from selenium import webdriver

import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

max_results = int(input('Enter number of display inbox message :'))
driver = webdriver.Chrome()
driver.maximize_window()
# OAuth 2.0 credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
flow = InstalledAppFlow.from_client_secrets_file('/home/arcgate/Downloads/credentials.json', SCOPES)
creds = None
token_path = 'token.json'

if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        creds = flow.run_local_server(port=0)
    with open(token_path, 'w') as token:
        token.write(creds.to_json())

# Gmail API
service = build('gmail', 'v1', credentials=creds)
results = service.users().messages().list(userId='me', labelIds=['INBOX'],maxResults=max_results).execute()
messages = results.get('messages', [])

# Read and print the subject of each email

# for message in messages:
#     msg = service.users().messages().get(userId='me', id=message['id']).execute()
#     # print(msg['payload']['parts'][1]['filename'])
#     headers = msg['payload']['headers']
#     for header in headers:
#         if header['name'] == 'Subject':
#             print(f"Subject: {header['value']}")
    
#     for part in msg['payload']['parts']:
#         filename = part.get('filename')

#         if part.get('body') and part['body'].get('attachmentId') and part['mimeType'].startswith('image/'):
#             attachment = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=part['body']['attachmentId']).execute()
#             data = base64.urlsafe_b64decode(attachment['data'])

#             with open(filename, 'wb') as f:
#                 f.write(data)
            
#             image = Image.open(filename)
#             text = pytesseract.image_to_string(image)
#             print(f"Text from image in {filename}: {text}")


for message in messages:
    msg = service.users().messages().get(userId='me', id=message['id']).execute()
    if 'payload' in msg and 'parts' in msg['payload']:
        image_attachments_exist = any(part.get('body') and part['body'].get('attachmentId') and part['mimeType'].startswith('image/') for part in msg['payload']['parts'])

        if image_attachments_exist:
            for part in msg['payload']['parts']:
                filename = part.get('filename')

                if part.get('body') and part['body'].get('attachmentId') and part['mimeType'].startswith('image/'):
                    attachment = service.users().messages().attachments().get(userId='me', messageId=message['id'], id=part['body']['attachmentId']).execute()
                    data = base64.urlsafe_b64decode(attachment['data'])

                    with open(filename, 'wb') as f:
                        f.write(data)

                    image = Image.open(filename)
                    text = pytesseract.image_to_string(image)
                    print(f"Text from image in {filename}: {text}")
                    
    else:
        headers = msg['payload']['headers']
        for header in headers:
            if header['name'] == 'Subject':
                print(f"Subject: {header['value']}")
            
driver.quit()
