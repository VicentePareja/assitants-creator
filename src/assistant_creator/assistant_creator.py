from openai import OpenAI
from parametros import NAME

class AssistantCreator:
    def __init__(self, api_key: str, instructions_path: str):
        self.client = OpenAI(api_key=api_key)
        self.instructions_path = instructions_path

    def load_instructions(self) -> str:
        with open(self.instructions_path, 'r', encoding='utf-8') as file:
            return file.read()

    def create_assistant(self, name_suffix: str, model: str, tools: list, temperature = float, max_tokens = int, top_p = float):
        instructions = self.load_instructions()
        name = f"{NAME}_{name_suffix}"
        print(f"Creating assistant with name: {name}")
        return self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=model,
            temperature=temperature,
            top_p=top_p
        )
