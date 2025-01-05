# name of the assitant
NAME = "House of Spencer"
# name models
FINE_TUNED_MODEL_WITHOUT_EXAMPLES_SUFIX = f"fine-tuned_whithout_examples"
FINE_TUNED_MODEL_WITH_EXAMPLES_SUFIX = f"fine-tuned_with_examples"
BASE_MODEL_SUFIX = f"base"
WITHOUT_EXAMPLES_MODEL_SUFIX = f"without_examples"


# base model for the assistants
BASE_MODEL = "gpt-4o-mini-2024-07-18"
TEMPERATURE = 0.5
TOP_P = 1


# Finetunning model
N_EPOCHS = 1

# evaluator model
EVAL_MODEL = "gpt-4o-mini-2024-07-18"
EVAL_TEMPERATURE = 0
EVAL_TOP_P = 0.5

QUESTION_COLUMN = "question"
HUMAN_RESPONSE_COLUMN = "human_response"



# routs
INSTRUCTIONS_PATH = f'data/original_instructions/{NAME}_original_instructions.txt'
TEXT_WITHOUT_EXAMPLES_PATH = f'data/separate_examples_from_text/{NAME}_text_without_examples.txt'
EXAMPLES_PATH = f'data/separate_examples_from_text/{NAME}_examples.txt'
JSONL_EXAMPLES_PATH = f'data/separate_examples_from_text/{NAME}_examples.jsonl'
ID_ASSISTANTS_PATH = f'data/assistants_ids/{NAME}_id_assistants.txt'
BASE_TEST_EXAMPLES_PATH = f'data/test/{NAME}_static_test_examples.txt'
BASE_TEST_RESULTS_PATH = f'data/test/{NAME}_static_test_results.csv'
INTRUCTIONS_STATIC_EVALUATOR_PATH = f'data/evaluator/{NAME}_static_evaluator_promt.txt'
ID_STATIC_EVALUATOR_PATH = f'data/assistants_ids/{NAME}_id_static_evaluator.txt'
CSV_STATIC_RESULTS_PATH = f'data/evaluator/{NAME}_static_evaluator_results.csv'