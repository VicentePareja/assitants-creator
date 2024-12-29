#file_importer.py
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from parametros import INSTRUCTIONS_PATH
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

class GoogleDocReader:
    def __init__(self, service_account_file, document_id):
        """
        Initialize the GoogleDocReader with a service account file and document ID.
        :param service_account_file: Path to the service account JSON file.
        :param document_id: ID of the Google Document to fetch.
        """
        self.service_account_file = service_account_file
        self.document_id = document_id
        self.credentials = None
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """
        Initialize the Google Docs API service using the service account credentials.
        """
        SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
        self.credentials = Credentials.from_service_account_file(
            self.service_account_file, scopes=SCOPES
        )
        self.service = build('docs', 'v1', credentials=self.credentials)

    def fetch_text(self):
        """
        Fetch the text content of the Google Document.
        :return: A string containing the document's text.
        """
        document = self.service.documents().get(documentId=self.document_id).execute()
        text = ''.join(
            element['textRun']['content']
            for content in document.get('body', {}).get('content', [])
            if 'paragraph' in content
            for element in content['paragraph']['elements']
            if 'textRun' in element
        )
        return text

if __name__ == '__main__':
    # Load environment variables
    load_dotenv()

    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    DOCUMENT_ID = os.getenv("DOCUMENT_ID")

    # Instantiate the GoogleDocReader class
    reader = GoogleDocReader(SERVICE_ACCOUNT_FILE, DOCUMENT_ID)

    # Fetch the document text
    doc_text = reader.fetch_text()

    # Save the document text to a .txt file

    with open(INSTRUCTIONS_PATH, "w", encoding="utf-8") as file:
        file.write(doc_text)

    print(f"Document text saved to {INSTRUCTIONS_PATH}")
