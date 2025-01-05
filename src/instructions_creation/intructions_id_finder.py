import json
import os
from dotenv import load_dotenv
import requests


class AssistantDocFinder:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.table_name = os.getenv("AIRTABLE_TABLE_NAME")

        if not all([self.api_key, self.base_id, self.table_name]):
            raise ValueError("Missing Airtable credentials in .env file.")

    def get_doc_id_by_assistant_name(self, assistant_name):
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {
            "filterByFormula": f"{{Name}}='{assistant_name}'"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if "records" in data and data["records"]:
                record = data["records"][0]  # Assuming one record per assistant name
                assistant_id = record["fields"].get("Assistant ID", "Not found")
                gdocs_address = record["fields"].get("GDocs Instruction Address", "Not found")
                return assistant_id, gdocs_address
            else:
                raise ValueError(f"No record found for assistant name '{assistant_name}'.")
        else:
            raise ConnectionError(f"Error: {response.status_code}, {response.text}")