import os
from dotenv import load_dotenv
from src.file_importer import GoogleDocReader
from src.text_separator import TextSeparator
from src.assistant_creator.assitant_creator import AssistantCreator
from parametros import INSTRUCTIONS_PATH, TEXT_WITHOUT_EXAMPLES_PATH, EXAMPLES_PATH

class DocumentImporter:
    def __init__(self, service_account_path: str, document_id: str, instructions_path: str):
        self.service_account_path = service_account_path
        self.document_id = document_id
        self.instructions_path = instructions_path

    def import_text(self):
        reader = GoogleDocReader(self.service_account_path, self.document_id)
        doc_text = reader.fetch_text()
        with open(self.instructions_path, "w", encoding="utf-8") as f:
            f.write(doc_text)
        print(f"Document text saved to {self.instructions_path}")

class TextSeparatorRunner:
    def __init__(self, api_key: str, assistant_id: str):
        self.api_key = api_key
        self.assistant_id = assistant_id

    def run(self):
        separator = TextSeparator(api_key=self.api_key, assistant_id=self.assistant_id)
        separator.run()

class Main:
    def __init__(self):
        load_dotenv()

        self.service_account_path = os.getenv("SERVICE_ACCOUNT_FILE")
        self.document_id = os.getenv("DOCUMENT_ID")
        self.base_instructions_path = INSTRUCTIONS_PATH
        self.intructions_without_examples_path = TEXT_WITHOUT_EXAMPLES_PATH
        self.examples_path = EXAMPLES_PATH

        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.assistant_id = os.getenv('ID_ASSISTANT_TEXT_SEPARATOR')

    def import_text_from_google_doc(self):
        importer = DocumentImporter(
            self.service_account_path,
            self.document_id,
            self.instructions_path
        )
        importer.import_text()

        separator_runner = TextSeparatorRunner(
            api_key=self.openai_api_key,
            assistant_id=self.assistant_id
        )
        separator_runner.run()

    def create_without_examples_assistant(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.intructions_without_examples_path
        )
        assistant = assistant_creator.create_assistant(
            name_suffix=" without examples",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}]
        )
        print(f"Assistant without examples created")

    def create_base_assistant(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.base_instructions_path
        )
        assistant = assistant_creator.create_assistant(
            name_suffix=" base",
            model="gpt-4o",
            tools=[{"type": "code_interpreter"}]
        )
        print(f"Base assistant created")

    def run(self):
        #self.import_text_from_google_doc()
        self.create_without_examples_assistant()
        self.create_base_assistant()

if __name__ == "__main__":
    main_app = Main()
    main_app.run()
