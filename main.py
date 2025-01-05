import os
import csv
from dotenv import load_dotenv
from src.instructions_creation.file_importer import DocumentImporter
from src.instructions_creation.text_separator import TextSeparatorRunner
from src.instructions_creation.intructions_id_finder import AssistantDocFinder
from src.assistant_creator.assistant_creator import AssistantCreator
from src.assistant_finetuner.examples_to_jsonl import TxtToJsonlConverter
from src.assistant_finetuner.create_finetune_model import OpenAIFineTuner
from src.assistant_finetuner.upload_jsonl import OpenAIFileUploader
from src.assistant_testing.static_test_creator import StaticExamplesTestCreator
from src.assistant_testing.static_assistant_tester import StaticAssistantsRunner
from src.assistant_testing.static_grader_results import FileManagerGrader


from parametros import (INSTRUCTIONS_PATH, TEXT_WITHOUT_EXAMPLES_PATH, EXAMPLES_PATH,
                        JSONL_EXAMPLES_PATH, NAME, BASE_MODEL, ID_ASSISTANTS_PATH, BASE_TEST_EXAMPLES_PATH,
                        BASE_TEST_RESULTS_PATH, INTRUCTIONS_STATIC_EVALUATOR_PATH, ID_STATIC_EVALUATOR_PATH, 
                        CSV_STATIC_RESULTS_PATH, TEMPERATURE, TOP_P, N_EPOCHS, EVAL_MODEL, EVAL_TEMPERATURE,
                        EVAL_TOP_P, FINE_TUNED_MODEL_WITHOUT_EXAMPLES_SUFIX, FINE_TUNED_MODEL_WITH_EXAMPLES_SUFIX,
                        BASE_MODEL_SUFIX, WITHOUT_EXAMPLES_MODEL_SUFIX, EVAL_STATIC_MODEL_NAME, FINE_TUNE_MODEL_SUFIX
)

class Main:
    def __init__(self):
        load_dotenv()

        
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
        self.temperature = TEMPERATURE
        self.top_p = TOP_P
        self.n_epochs = N_EPOCHS
        self.eval_model = EVAL_MODEL
        self.eval_temperature = EVAL_TEMPERATURE
        self.eval_top_p = EVAL_TOP_P

        self.service_account_path = os.getenv("SERVICE_ACCOUNT_FILE")
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.assistant_id = os.getenv('ID_ASSISTANT_TEXT_SEPARATOR')

        self.fine_tuner = OpenAIFineTuner(api_key=self.openai_api_key)
        self.static_test_creator = StaticExamplesTestCreator(input_test_file=EXAMPLES_PATH, 
                                                          output_test_file=BASE_TEST_EXAMPLES_PATH)
        self.static_assistant_runner = StaticAssistantsRunner(openai_api_key=self.openai_api_key, 
                                                          txt_file_path=self.assistant_id_path, 
                                                          csv_file_path=BASE_TEST_EXAMPLES_PATH, 
                                                          output_csv_path=self.base_test_results_path)

    def find_doc_id(self, assistant_name):
        finder = AssistantDocFinder()
        assistant_id, gdocs_address = finder.get_doc_id_by_assistant_name(assistant_name)
        self.document_id = gdocs_address

        print(f"document with assistant's instructions found")

    def import_text_from_google_doc(self):
        importer = DocumentImporter(
            self.service_account_path,
            self.document_id,
            self.base_instructions_path
        )
        importer.import_text()

    def separate_text(self):

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
            name_suffix=WITHOUT_EXAMPLES_MODEL_SUFIX,
            model=BASE_MODEL,
            tools=[],
            temperature=self.temperature,
            top_p=self.top_p
        )
        self.save_assistant_id(self.without_examples_assistant.name,
                                self.without_examples_assistant.id,
                                self.assistant_id_path)

    def create_base_assistant(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.base_instructions_path
        )
        self.base_assistant = assistant_creator.create_assistant(
            name_suffix=BASE_MODEL_SUFIX,
            model=BASE_MODEL,
            tools=[],
            temperature=self.temperature,
            top_p=self.top_p
        )
        self.save_assistant_id(self.base_assistant.name,
                               self.base_assistant.id,
                               self.assistant_id_path)


    def upload_jsonl_to_openai(self):
        uploader = OpenAIFileUploader(api_key=self.openai_api_key)
        response = uploader.upload_file(
            file_path=self.jsonl_examples_path,
            purpose="fine-tune and test new models."
        )
        print("Jsonl file uploaded successfully!")
        self.fine_tune_file_id = response.id

    def create_fine_tune_model(self):
        response = self.fine_tuner.create_fine_tuning_job(
            training_file_id=self.fine_tune_file_id,
            model=BASE_MODEL,
            suffix=f"{NAME}_{FINE_TUNE_MODEL_SUFIX}"
        )
        fine_tune_job_id = response.id
        self.fine_tune_model = self.fine_tuner.monitor_fine_tuning_job(fine_tune_job_id)

    def create_fine_tune_assistant_without_examples(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.intructions_without_examples_path
        )
        self.fine_tune_assistant_without_examples = assistant_creator.create_assistant(
            name_suffix=FINE_TUNED_MODEL_WITHOUT_EXAMPLES_SUFIX,
            model=self.fine_tune_model,
            tools=[],
            temperature=self.temperature,
            top_p=self.top_p
        )
        self.save_assistant_id(self.fine_tune_assistant_without_examples.name,
                               self.fine_tune_assistant_without_examples.id,
                               self.assistant_id_path)

    def create_fine_tune_assistant_with_examples(self):
        assistant_creator = AssistantCreator(
            api_key=self.openai_api_key,
            instructions_path=self.base_instructions_path
        )
        self.fine_tune_assistant_with_examples = assistant_creator.create_assistant(
            name_suffix=FINE_TUNED_MODEL_WITH_EXAMPLES_SUFIX,
            model=self.fine_tune_model,
            tools=[],
            temperature=self.temperature,
            top_p=self.top_p
        )
        self.save_assistant_id(self.fine_tune_assistant_with_examples.name,
                               self.fine_tune_assistant_with_examples.id,
                               self.assistant_id_path)

    def prepare_fine_tune_assistants(self):
        self.create_jsonl_for_finetuning()
        self.upload_jsonl_to_openai()
        self.create_fine_tune_model()

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
            name_suffix=EVAL_STATIC_MODEL_NAME,
            model=EVAL_MODEL,
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
        """
        Crea un archivo CSV unificado que incluye:
            - Todas las columnas del CSV base (self.base_test_results_path).
            - Tres columnas adicionales: 
                grade_without_examples, grade_base, grade_fine_tuned
            - Se asume que la posición (index) de la fila en el CSV de 'grade'
            corresponde a la misma en el CSV base. 
        """

        # 1) Leemos el CSV base en memoria
        if not os.path.exists(self.base_test_results_path):
            print(f"No existe el archivo base en: {self.base_test_results_path}")
            return

        main_rows = []
        with open(self.base_test_results_path, 'r', encoding='utf-8') as f_base:
            reader = csv.DictReader(f_base)
            for row in reader:
                main_rows.append(row)

        if not main_rows:
            print(f"El archivo base {self.base_test_results_path} está vacío.")
            return

        # 2) Helper para leer un CSV de una sola columna "grade" como lista
        def read_grades_as_list(csv_path, grade_col='grade'):
            grades_list = []
            if not os.path.exists(csv_path):
                print(f"El archivo {csv_path} no existe.")
                return grades_list  # lista vacía
            with open(csv_path, 'r', encoding='utf-8') as f_in:
                reader = csv.DictReader(f_in)
                for row in reader:
                    g_val = row.get(grade_col, "").strip()
                    grades_list.append(g_val)
            return grades_list

        # 3) Construimos las tres listas de 'grade'
        grades_no_examples = read_grades_as_list('data/evaluator/static_results_without_examples.csv')
        grades_base        = read_grades_as_list('data/evaluator/static_results_base.csv')
        grades_fine_tuned  = read_grades_as_list('data/evaluator/static_results_fine-tuned.csv')

        # 4) Definimos el nombre de las nuevas columnas y el CSV unificado
        output_file_unified = 'data/evaluator/unified_results.csv'
        new_columns = [
            "grade_without_examples",
            "grade_base",
            "grade_fine_tuned"
        ]

        fieldnames = list(main_rows[0].keys()) + new_columns

        # 5) Escribimos el CSV unificado
        with open(output_file_unified, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            # Chequeo de tamaños (opcional)
            num_base_rows = len(main_rows)
            if not (
                len(grades_no_examples) == num_base_rows and
                len(grades_base) == num_base_rows and
                len(grades_fine_tuned) == num_base_rows
            ):
                print("Advertencia: El número de filas en los CSV de 'grade' no coincide con el base.")
                print(f"Base: {num_base_rows}, no_examples: {len(grades_no_examples)}, "
                    f"base: {len(grades_base)}, fine_tuned: {len(grades_fine_tuned)}")

            # Unificamos fila por fila usando la posición (i)
            for i, row in enumerate(main_rows):
                # Verificamos que i no exceda la cantidad de filas en la lista 
                row["grade_without_examples"] = grades_no_examples[i] if i < len(grades_no_examples) else ""
                row["grade_base"]            = grades_base[i]        if i < len(grades_base) else ""
                row["grade_fine_tuned"]      = grades_fine_tuned[i]  if i < len(grades_fine_tuned) else ""

                writer.writerow(row)

        print(f"Archivo unificado creado en: {output_file_unified}")

    def create_instructions(self):
        self.find_doc_id(self.name)
        self.import_text_from_google_doc()
        self.separate_text()

    def create_assistants(self):
        self.create_without_examples_assistant()
        self.create_base_assistant()
        self.prepare_fine_tune_assistants()
        self.create_fine_tune_assistant_without_examples()
        self.create_fine_tune_assistant_with_examples()

    def eval_models(self):
        self.create_static_tests()
        self.generate_static_test_answers()
        self.create_static_evaluator_assistant()
        self.grade_static_tests()
        self.generate_unified_csv_results()

    def run(self):
        #self.create_instructions()
        #self.create_assistants() 
        self.eval_models()

if __name__ == "__main__":
    main_app = Main()
    main_app.run()
