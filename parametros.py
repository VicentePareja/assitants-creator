# name of the assitant
NAME = "HOS"

# base model for the assistants
BASE_MODEL = "gpt-4o-mini-2024-07-18"


# Finetunning model
N_EPOCHS = 1


# routs
INSTRUCTIONS_PATH = f'separate_examples_from_text/{NAME}original_instructions.txt'
TEXT_WITHOUT_EXAMPLES_PATH = f'separate_examples_from_text/{NAME}text_without_examples.txt'
EXAMPLES_PATH = f'separate_examples_from_text/{NAME}examples.txt'
JSONL_EXAMPLES_PATH = f'separate_examples_from_text/{NAME}examples.jsonl'