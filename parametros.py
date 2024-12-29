# name of the assitant
NAME = "HOS"

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