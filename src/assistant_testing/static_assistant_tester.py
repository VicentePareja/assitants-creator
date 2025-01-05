import sys
sys.stdout.reconfigure(encoding='utf-8')  # Ensure UTF-8 output

import os
import re
import csv
from dotenv import load_dotenv
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from tqdm import tqdm  # <-- for the progress bar
from parametros import QUESTION_COLUMN, HUMAN_RESPONSE_COLUMN

class EventHandler(AssistantEventHandler):
    """Event handler to stream responses from the assistant in real time."""
    @override
    def on_text_created(self, text) -> None:
        # Using UTF-8 safe print
        #print("\nassistant > ", end="", flush=True)
        pass
    @override
    def on_text_delta(self, delta, snapshot):
        # Encode-decode to ensure safe printing of unicode chars
        safe_output = delta.value.encode('utf-8', 'replace').decode('utf-8')
        #print(safe_output, end="", flush=True)
    
    def on_tool_call_created(self, tool_call):
        #print(f"\nassistant > {tool_call.type}\n", flush=True)
        pass
    
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                input_str = delta.code_interpreter.input.encode('utf-8', 'replace').decode('utf-8')
                print(input_str, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
            for output in delta.code_interpreter.outputs:
                if output.type == "logs":
                    logs_str = output.logs.encode('utf-8', 'replace').decode('utf-8')
                    print(f"\n{logs_str}", flush=True)

class StaticAssistantsRunner:
    """
    A class that:
      1) Reads assistant names and IDs from a .txt file.
      2) Reads questions and human answers from a .csv file.
      3) Queries each assistant with each question.
      4) Produces a new .csv file with columns: question,human_answer,<assistant_1_name>,...
    """

    def __init__(self, openai_api_key: str, txt_file_path: str, csv_file_path: str, output_csv_path: str):
        """
        :param openai_api_key: OpenAI API key.
        :param txt_file_path: Path to the .txt file containing (assistant_name, assistant_id) lines.
        :param csv_file_path: Path to the .csv file with columns question,human_answer.
        :param output_csv_path: Path to write the output .csv file with question,human_answer,<assistant_1_name>,...
        """
        self.openai_api_key = openai_api_key
        self.txt_file_path = txt_file_path
        self.csv_file_path = csv_file_path
        self.output_csv_path = output_csv_path
        self.assistants_dict = {}
        self.qa_data = []

    def load_assistants(self):
        """
        Reads the .txt file and extracts lines of the form:
            ('Assistant Name', 'assistant_id')
        Stores results in self.assistants_dict as {assistant_name: assistant_id}.
        """
        if not os.path.exists(self.txt_file_path):
            print(f"Error: The file {self.txt_file_path} does not exist.")
            return

        pattern = re.compile(r"\('([^']+)',\s*'([^']+)'\)")
        with open(self.txt_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Match lines of the form ('something','something')
                match = pattern.match(line)
                if match:
                    assistant_name = match.group(1)
                    assistant_id = match.group(2)
                    self.assistants_dict[assistant_name] = assistant_id

        print(f"Loaded {len(self.assistants_dict)} assistants from {self.txt_file_path}:")
        for name, asst_id in self.assistants_dict.items():
            print(f"  {name}")

    def load_qa_data(self):
        """
        Reads the CSV file containing question,human_answer
        and stores it in a list of dicts: [{'question':..., 'human_answer':...}, ...].
        """
        if not os.path.exists(self.csv_file_path):
            print(f"Error: The file {self.csv_file_path} does not exist.")
            return

        with open(self.csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                question = row.get(QUESTION_COLUMN, "").strip()
                human_answer = row.get(HUMAN_RESPONSE_COLUMN, "").strip()
                self.qa_data.append({QUESTION_COLUMN: question, HUMAN_RESPONSE_COLUMN: human_answer})

        print(f"Loaded {len(self.qa_data)} Q&A rows from {self.csv_file_path}.")

    def run_assistant(self, assistant_id: str, prompt: str) -> str:
        """
        Queries an assistant with a given prompt and returns the assistant's response as text.
        """
        client = OpenAI(api_key=self.openai_api_key)
        value_pattern = re.compile(r"value='([^']*)'")

        try:
            thread = client.beta.threads.create()
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            # Stream the assistant's response
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=assistant_id,
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()
            
            # Retrieve messages from the thread
            response_message = client.beta.threads.messages.list(thread_id=thread.id)
            if response_message and response_message.data:
                # Collect all assistant messages
                assistant_responses = [
                    msg.content for msg in response_message.data if msg.role == 'assistant'
                ]
                if assistant_responses:
                    last_response = assistant_responses[-1]
                    # Handle if the response is not a simple string
                    if not isinstance(last_response, str):
                        if isinstance(last_response, list):
                            last_response_str = " ".join(str(item) for item in last_response)
                        else:
                            last_response_str = str(last_response)
                    else:
                        last_response_str = last_response

                    # Optional extraction pattern
                    match = value_pattern.search(last_response_str)
                    if match:
                        # If you want to extract some substring, use match.group(1)
                        return match.group(1)
                    else:
                        return last_response_str
                else:
                    return "No response from assistant."
            else:
                return "No response from assistant."
        except Exception as e:
            print(f"Error running prompt '{prompt}' with assistant {assistant_id}: {e}")
            return f"Error: {e}"

    def run_all(self):
        """
        Main method that:
         1) Loads assistants
         2) Loads QA data
         3) For each QA row, queries each assistant
         4) Writes a CSV with columns: question, human_answer, <assistant_1>, ...
         5) Shows a progress bar using tqdm.
        """
        # Step 1: load all assistants from txt file
        self.load_assistants()
        # Step 2: load Q&A data from CSV
        self.load_qa_data()

        if not self.assistants_dict or not self.qa_data:
            print("No assistants or QA data found. Exiting.")
            return

        # Prepare the output CSV columns
        fieldnames = [QUESTION_COLUMN, HUMAN_RESPONSE_COLUMN] + list(self.assistants_dict.keys())

        try:
            with open(self.output_csv_path, 'w', newline='', encoding='utf-8') as out_f:
                writer = csv.DictWriter(out_f, fieldnames=fieldnames)
                writer.writeheader()

                # Use a tqdm progress bar for the Q&A processing:
                with tqdm(total=len(self.qa_data), desc="Processing QA pairs") as pbar:
                    for idx, item in enumerate(self.qa_data, start=1):
                        row = {
                            QUESTION_COLUMN: item[QUESTION_COLUMN],
                            HUMAN_RESPONSE_COLUMN: item[HUMAN_RESPONSE_COLUMN],
                        }

                        # Query each assistant
                        for asst_name, asst_id in self.assistants_dict.items():
                            answer = self.run_assistant(asst_id, item[QUESTION_COLUMN])
                            row[asst_name] = answer

                        # Write the row to the output CSV
                        writer.writerow(row)

                        # Update the progress bar
                        pbar.update(1)

            print(f"\nAll done! Results saved to {self.output_csv_path}\n")
        except Exception as e:
            print(f"Error creating output CSV {self.output_csv_path}: {e}")