from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
DOCUMENT_ID = os.getenv("DOCUMENT_ID")

def fetch_google_doc_text(document_id):
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('docs', 'v1', credentials=credentials)
    document = service.documents().get(documentId=document_id).execute()
    text = ''.join(
        element['textRun']['content']
        for content in document.get('body', {}).get('content', [])
        if 'paragraph' in content
        for element in content['paragraph']['elements']
        if 'textRun' in element
    )
    return text

if __name__ == '__main__':
    doc_text = fetch_google_doc_text(DOCUMENT_ID)
    print("Document Text:")
    print(doc_text)
