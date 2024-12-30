import json
import csv

class StaticExamplesTestCreator:
    def __init__(self, input_test_file, output_test_file):
        self.input_test_file = input_test_file
        self.output_test_file = output_test_file

    def create_test(self):
        # Read the JSON-like file
        with open(self.input_test_file, "r", encoding="utf-8") as file:
            data = json.load(file)  # Parse the JSON data

        # Write to the CSV file
        with open(self.output_test_file, "w", newline='', encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            # Write the headers
            writer.writerow(["question", "human_answer"])
            
            # Write each question-answer pair 4 times
            for entry in data:
                for _ in range(4):  # Repeat each pair 4 times
                    writer.writerow([entry["Q"], entry["A"]])

        print(f"Base Test file created: {self.output_test_file}")
