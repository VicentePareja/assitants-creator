# name of the assitant
NAME = "HOS"
# name models
FINE_TUNED_MODEL_NAME = f"{NAME}fine-tuned"
BASE_MODEL_NAME = f"{NAME}base"
WITHOUT_EXAMPLES_MODEL_NAME = f"{NAME}without_examples"


# base model for the assistants
BASE_MODEL = "gpt-4o-mini-2024-07-18"


# Finetunning model
N_EPOCHS = 1


# routs
INSTRUCTIONS_PATH = f'data/original_instructions/{NAME}original_instructions.txt'
TEXT_WITHOUT_EXAMPLES_PATH = f'data/separate_examples_from_text/{NAME}text_without_examples.txt'
EXAMPLES_PATH = f'data/separate_examples_from_text/{NAME}examples.txt'
JSONL_EXAMPLES_PATH = f'data/separate_examples_from_text/{NAME}examples.jsonl'
ID_ASSISTANTS_PATH = f'data/assistants_ids/{NAME}id_assistants.txt'
BASE_TEST_EXAMPLES_PATH = f'data/test/{NAME}static_test_examples.txt'
BASE_TEST_RESULTS_PATH = f'data/test/{NAME}static_test_results.csv'
INTRUCTIONS_STATIC_EVALUATOR_PATH = f'data/evaluator/{NAME}static_evaluator_promt.txt'
ID_STATIC_EVALUATOR_PATH = f'data/assistants_ids/{NAME}id_static_evaluator.txt'
CSV_STATIC_RESULTS_PATH = f'data/evaluator/{NAME}static_evaluator_results.csv'