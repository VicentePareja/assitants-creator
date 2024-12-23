# main.py

import os
from dotenv import load_dotenv
from file_importer import GoogleDocReader
from text_separator import TextSeparator
from parametros import INSTRUCTIONS_PATH

def main():
    # Load environment variables
    load_dotenv()

    # -------------------------------------------------------------------------
    # 1. Fetch text from Google Doc and save to instructions file
    # -------------------------------------------------------------------------
    # The environment might store these (SERVICE_ACCOUNT_FILE, DOCUMENT_ID) 
    # or you can rely on parametros.py if you’ve put them there.
    service_account_path = os.getenv("SERVICE_ACCOUNT_FILE")
    document_id = os.getenv("DOCUMENT_ID")

    # Instantiate the reader and fetch doc text
    reader = GoogleDocReader(service_account_path, document_id)
    doc_text = reader.fetch_text()

    # Write to the instructions file
    with open(INSTRUCTIONS_PATH, "w", encoding="utf-8") as f:
        f.write(doc_text)
    print(f"Document text saved to {INSTRUCTIONS_PATH}")

    # -------------------------------------------------------------------------
    # 2. Run the TextSeparator to parse instructions and extract JSON
    # -------------------------------------------------------------------------
    openai_api_key = os.getenv('OPENAI_API_KEY')
    known_assistant_id = os.getenv('ID_ASSISTANT_TEXT_SEPARATOR')

    # Instantiate and run TextSeparator
    separator = TextSeparator(api_key=openai_api_key, assistant_id=known_assistant_id)
    separator.run()


if __name__ == "__main__":
    main()
