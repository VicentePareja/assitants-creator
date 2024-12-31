import os
import csv
from dotenv import load_dotenv
from src.instructions_creation.file_importer import GoogleDocReader
from src.instructions_creation.text_separator import TextSeparator
from src.assistant_creator.assitant_creator import AssistantCreator
from src.assitant_finetuner.examples_to_jsonl import TxtToJsonlConverter
from src.assitant_finetuner.create_finetune_model import OpenAIFineTuner
from src.assitant_finetuner.upload_jsonl import OpenAIFileUploader
from src.assistant_testing.static_test_creator import StaticExamplesTestCreator
from src.assistant_testing.static_assistant_tester import StaticAssistantsRunner
from src.assistant_testing.static_grader_results import FileManagerGrader


from parametros import (INSTRUCTIONS_PATH, TEXT_WITHOUT_EXAMPLES_PATH, EXAMPLES_PATH,
                        JSONL_EXAMPLES_PATH, NAME, BASE_MODEL, ID_ASSISTANTS_PATH, BASE_TEST_EXAMPLES_PATH,
                        BASE_TEST_RESULTS_PATH, INTRUCTIONS_STATIC_EVALUATOR_PATH, ID_STATIC_EVALUATOR_PATH, 
                        CSV_STATIC_RESULTS_PATH)

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
        self.name = NAME
        self.assistant_id_path = ID_ASSISTANTS_PATH
        self.base_instructions_path = INSTRUCTIONS_PATH
        self.intructions_without_examples_path = TEXT_WITHOUT_EXAMPLES_PATH
        self.examples_path = EXAMPLES_PATH
        self.jsonl_examples_path = JSONL_EXAMPLES_PATH
        self.promt_path = TEXT_WITHOUT_EXAMPLES_PATH
        self.base_test_results_path = BASE_TEST_RESULTS_PATH
        self.static_evaluator_promt_path = INTRUCTIONS_STATIC_EVALUATOR_PATH
        self.static_evaluator_id_path = ID_STATIC_EVALUATOR_PATH
        self.static_results_path = CSV_STATIC_RESULTS_PATH

        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.assistant_id = os.getenv('ID_ASSISTANT_TEXT_SEPARATOR')

        self.fine_tuner = OpenAIFineTuner(api_key=self.openai_api_key)
        self.static_test_creator = StaticExamplesTestCreator(input_test_file=EXAMPLES_PATH, 
                                                          output_test_file=BASE_TEST_EXAMPLES_PATH)
        self.static_assistant_runner = StaticAssistantsRunner(openai_api_key=self.openai_api_key, 
                                                          txt_file_path=self.assistant_id_path, 
                                                          csv_file_path=BASE_TEST_EXAMPLES_PATH, 
                                                          output_csv_path=self.base_test_results_path)

    def import_text_from_google_doc(self):
        importer = DocumentImporter(
            self.service_account_path,
            self.document_id,
            self.base_instructions_path
        )
        importer.import_text()

        separator_runner = TextSeparatorRunner(
            api_key=self.openai_api_key,
            assistant_id=self.assistant_id
        )
        separator_runner.run()

    def save_assistant_id(self, assistant_name, assistant_id: str, path):
        with open(self.assistant_id_path, "a", encoding="utf-8") as f:
            f.write(f"{assistant_name, assistant_id}\n")

    def create_jsonl_for_finetuning(self):
        txt_to_jsonl_converter = TxtToJsonlConverter(
            input_examples_txt_path=self.examples_path,
            input_prompt_txt=self.promt_path,
            output_jsonl_path=self.jsonl_examples_path
        )
        txt_to_jsonl_converter.convert()


    def create_without_examples_assistant(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.intructions_without_examples_path
        )
        self.without_examples_assistant = assistant_creator.create_assistant(
            name_suffix=" without examples",
            model=BASE_MODEL,
            tools=[{"type": "code_interpreter"}]
        )
        self.save_assistant_id(self.without_examples_assistant.name, self.without_examples_assistant.id)

    def create_base_assistant(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.base_instructions_path
        )
        self.base_assistant = assistant_creator.create_assistant(
            name_suffix=" base",
            model=BASE_MODEL,
            tools=[{"type": "code_interpreter"}]
        )
        self.save_assistant_id(self.base_assistant.name, self.base_assistant.id)


    def upload_jsonl_to_openai(self):
        uploader = OpenAIFileUploader(api_key=self.openai_api_key)
        response = uploader.upload_file(
            file_path=self.jsonl_examples_path,
            purpose="fine-tune"
        )
        print("Jsonl file uploaded successfully!")
        self.fine_tune_file_id = response.id

    def create_fine_tune_model(self):
        response = self.fine_tuner.create_fine_tuning_job(
            training_file_id=self.fine_tune_file_id,
            model=BASE_MODEL,
            suffix=f"{NAME}fine-tuned"
        )
        fine_tune_job_id = response.id
        self.fine_tune_model = self.fine_tuner.monitor_fine_tuning_job(fine_tune_job_id)

    def create_fine_tune_assistant(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.intructions_without_examples_path
        )
        self.fine_tune_assistant = assistant_creator.create_assistant(
            name_suffix=" fine-tuned",
            model=self.fine_tune_model,
            tools=[{"type": "code_interpreter"}]
        )
        self.save_assistant_id(self.fine_tune_assistant.name, self.fine_tune_assistant.id)

    def create_fine_tune_assitant_without_examples(self):
        self.create_jsonl_for_finetuning()
        self.upload_jsonl_to_openai()
        self.create_fine_tune_model()
        self.create_fine_tune_assistant()

    def create_static_tests(self):
        self.static_test_creator.create_test()

    def generate_static_test_answers(self):
        self.static_assistant_runner.run_all()

    def create_static_evaluator_assistant(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.static_evaluator_promt_path
        )
        self.evaluator_assistant = assistant_creator.create_assistant(
            name_suffix="static evaluator",
            model=BASE_MODEL,
            tools=[{"type": "code_interpreter"}]
        )
        with open(self.static_evaluator_id_path, "a", encoding="utf-8") as f:
            f.write(f"{self.evaluator_assistant.name, self.evaluator_assistant.id}\n")

    def grade_static_tests(self):

        evaluator_id = "asst_yZVY7g4Pyj8ALkwL3bO1SoYk"    

        self.static_evaluator = FileManagerGrader(openai_api_key=self.openai_api_key,
                                                  assistant_id=evaluator_id,
                                                  csv_input_path=self.base_test_results_path)
        
        self.static_evaluator.run(question_column="question", human_answer_column="human_answer", 
                                  machine_answer_column="HOS  without examples", output_csv_path='data/evaluator/static_results_without_examples.csv')
        
        self.static_evaluator.run(question_column="question", human_answer_column="human_answer", 
                                  machine_answer_column="HOS  base", output_csv_path='data/evaluator/static_results_base.csv')
        
        self.static_evaluator.run(question_column="question", human_answer_column="human_answer", 
                                  machine_answer_column="HOS  fine-tuned", output_csv_path='data/evaluator/static_results_fine-tuned.csv')
        
    def generate_unified_csv_results(self):

        """        Crea un archivo CSV unificado que incluye:
            - Todas las columnas del CSV base (self.base_test_results_path).
            - Tres columnas adicionales, con los 'grade' de cada archivo:
                grade_without_examples
                grade_base
                grade_fine_tuned
            Se asume que 'question' es la columna que identifica cada fila en común"""

        # 1) Leemos el CSV base en memoria
        main_rows = []
        if not os.path.exists(self.base_test_results_path):
            print(f"No existe el archivo base en: {self.base_test_results_path}")
            return
        
        with open(self.base_test_results_path, 'r', encoding='utf-8') as f_base:
            reader = csv.DictReader(f_base)
            for row in reader:
                main_rows.append(row)
        
        if not main_rows:
            print(f"El archivo base {self.base_test_results_path} está vacío.")
            return
        
        # 2) Leemos los 3 archivos donde guardaste 'grade', usando un helper
        #    que retorne un diccionario { question_val : grade_val }.
        def read_grades_to_dict(csv_path, question_col='question', grade_col='grade'):
            grades_dict = {}
            if not os.path.exists(csv_path):
                print(f"El archivo {csv_path} no existe.")
                return grades_dict  # diccionario vacío
            with open(csv_path, 'r', encoding='utf-8') as f_in:
                reader = csv.DictReader(f_in)
                for row in reader:
                    # Ajusta la lógica si tu 'question' está en otra columna
                    q_val = row.get(question_col, "").strip()
                    g_val = row.get(grade_col, "").strip()
                    if q_val:
                        grades_dict[q_val] = g_val
            return grades_dict

        # 3) Construimos los 3 diccionarios a partir de los CSV con 1 sola columna "grade"
        grades_no_examples = read_grades_to_dict('data/evaluator/static_results_without_examples.csv')
        grades_base        = read_grades_to_dict('data/evaluator/static_results_base.csv')
        grades_fine_tuned  = read_grades_to_dict('data/evaluator/static_results_fine-tuned.csv')

        # 4) Definimos el nombre de las nuevas columnas y el CSV unificado.
        output_file_unified = 'data/evaluator/unified_results.csv'
        new_columns = [
            "grade_without_examples",
            "grade_base",
            "grade_fine_tuned"
        ]

        # Las columnas originales + las 3 nuevas
        fieldnames = list(main_rows[0].keys()) + new_columns

        # 5) Unimos todo en un solo CSV
        with open(output_file_unified, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            # Recorremos cada fila del CSV base y completamos las 3 nuevas columnas
            for row in main_rows:
                question_val = row.get('question', "").strip()

                row["grade_without_examples"] = grades_no_examples.get(question_val, "")
                row["grade_base"]            = grades_base.get(question_val, "")
                row["grade_fine_tuned"]      = grades_fine_tuned.get(question_val, "")

                writer.writerow(row)

        print(f"Archivo unificado creado en: {output_file_unified}")


    def create_assistants(self):
        self.create_without_examples_assistant()
        self.create_base_assistant()
        self.create_fine_tune_assitant_without_examples()

    def eval_models(self):
        self.create_static_tests()
        self.generate_static_test_answers()
        self.create_static_evaluator_assistant()
        self.grade_static_tests()
        self.generate_unified_csv_results()

    def run(self):
        self.import_text_from_google_doc()
        self.create_assistants() 
        self.eval_models()


if __name__ == "__main__":
    main_app = Main()
    main_app.run()
