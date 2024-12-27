import os
from pathlib import Path
from openai import OpenAI

class OpenAIFileUploader:
    def __init__(self, api_key: str):
        """
        Initialize the OpenAIFileUploader with the API key.
        """
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def upload_file(self, file_path: str, purpose: str) -> dict:
        """
        Upload a file to OpenAI.

        Args:
            file_path (str): Path to the file to be uploaded.
            purpose (str): The purpose of the file upload (e.g., "fine-tune").

        Returns:
            dict: The response from the OpenAI API.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        try:
            response = self.client.files.create(
                file=Path(file_path),
                purpose=purpose,
            )
            return response
        except Exception as e:
            print(f"An error occurred while uploading the file: {e}")
            raise

# Example usage:
if __name__ == "__main__":
    api_key = "your_openai_api_key_here"  # Replace with your API key
    uploader = OpenAIFileUploader(api_key)
    
    file_path = "input.jsonl"  # Replace with your file path
    purpose = "fine-tune"      # Specify the purpose for the file upload

    try:
        response = uploader.upload_file(file_path, purpose)
        print("File uploaded successfully!")
        print(response)
    except Exception as e:
        print(f"Failed to upload the file: {e}")
