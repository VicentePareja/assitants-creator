# HOS Assistant Creation and Evaluation

This project automates the creation, fine-tuning, and evaluation of AI assistants based on OpenAI's language models. It provides a pipeline to generate assistants with different configurations, test their performance, and grade their outputs for quality.

## Project Structure

```
ASSISTANTS-CREATOR/
├── __pycache__/
├── data/
│   ├── assistant_responses/
│   ├── assistants_ids/
│   │   └── HOSid_assistants.txt
│   ├── separate_examples_from_text/
│   │   ├── HOSexamples.jsonl
│   │   ├── HOSexamples.txt
│   │   ├── HOStext_without_examples.txt
│   ├── evaluator/
│   │   ├── HOSstatic_evaluator_results.csv
│   │   ├── unified_results.csv
│   ├── test/
│   │   ├── HOSstatic_test_examples.txt
│   │   ├── HOSstatic_test_results.csv
├── src/
│   ├── instructions_creation/
│   │   ├── file_importer.py
│   │   ├── text_separator.py
│   ├── assistant_creator/
│   │   └── assistant_creator.py
│   ├── assistant_finetuner/
│   │   ├── create_finetune_model.py
│   │   ├── examples_to_jsonl.py
│   │   ├── upload_jsonl.py
│   ├── assistant_testing/
│   │   ├── static_test_creator.py
│   │   ├── static_assistant_tester.py
│   │   ├── static_grader_results.py
├── main.py
├── parametros.py
├── .env
```

## Key Components

### 1. **Instructions Creation**
- **GoogleDocReader**: Imports instructions from Google Docs.
- **TextSeparator**: Separates examples from the main instruction text.

### 2. **Assistant Creation**
- **AssistantCreator**: Creates OpenAI-based assistants using various instruction sets and configurations.
- **Finetuning**:
  - Converts example text to JSONL.
  - Uploads training data to OpenAI.
  - Fine-tunes the base model.

### 3. **Assistant Testing**
- **StaticExamplesTestCreator**: Generates static test sets from provided examples.
- **StaticAssistantsRunner**: Runs test cases on created assistants and collects results.

### 4. **Evaluation**
- **FileManagerGrader**: Grades assistant outputs against human-provided answers.
- **Unified CSV Results**: Combines test results and grades into a unified CSV for analysis.

## Features

1. **Assistant Variants**:
   - **Base Assistant**: Uses the original instructions.
   - **Without Examples Assistant**: Uses instructions without examples.
   - **Fine-Tuned Assistant**: Uses a fine-tuned model.

2. **Automated Testing**:
   - Static tests are run across all assistant variants.
   - Results are graded and stored in CSV files.

3. **Evaluation Metrics**:
   - Assistants are graded by comparing their outputs to human answers.
   - Results are unified into a single CSV for easier analysis.

## Setup

### Prerequisites
- Python 3.10+
- OpenAI API key
- Google service account credentials
- `.env` file for sensitive information

### Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd ASSISTANTS-CREATOR
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following content:
   ```env
   OPENAI_API_KEY=<your_openai_api_key>
   SERVICE_ACCOUNT_FILE=<path_to_google_service_account_json>
   DOCUMENT_ID=<google_doc_id>
   ID_ASSISTANT_TEXT_SEPARATOR=<assistant_id>
   ```

## Usage

1. **Run the Main Script**:
   ```bash
   python main.py
   ```

2. **Pipeline Steps**:
   - Import instructions from Google Docs.
   - Create assistants:
     - Without examples
     - Base assistant
     - Fine-tuned assistant
   - Generate and evaluate static tests.

3. **Results**:
   - Check assistant IDs in `data/assistants_ids/`.
   - Review test results in `data/test/`.
   - Analyze unified grades in `data/evaluator/unified_results.csv`.

## Parameters
Defined in `parametros.py`:

- `NAME`: Assistant name.
- `BASE_MODEL`: Base OpenAI model to use.
- Paths for instructions, examples, JSONL files, test results, and evaluation results.

## File Outputs

### Assistants
- `data/assistants_ids/`: Stores IDs of created assistants.

### Tests
- `data/test/`: Contains static test examples and results.

### Evaluation
- `data/evaluator/`: Contains graded results and the unified results CSV.

## Extending the Project

1. **Adding New Tests**:
   - Update `StaticExamplesTestCreator` with additional test cases.

2. **Supporting More Models**:
   - Modify `parametros.py` to include new model configurations.

3. **Custom Grading Logic**:
   - Enhance `FileManagerGrader` with new grading criteria.

## Contributing
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/new-feature
   ```
3. Commit changes:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/new-feature
   ```
5. Create a pull request.

## License
This project is licensed under the MIT License.