import json

class TxtToJsonlConverter:
    def __init__(self, input_examples_txt_path, input_prompt_txt, output_jsonl_path):
        self.input_txt_path = input_examples_txt_path
        self.output_jsonl_path = output_jsonl_path
        self.input_prompt_txt = input_prompt_txt
    
    def convert(self):
        try:
            # Leer el archivo .txt
            with open(self.input_txt_path, 'r', encoding='utf-8') as txt_file:
                data = json.load(txt_file)  # Leer el contenido como JSON

            with open(self.input_prompt_txt, 'r', encoding='utf-8') as txt_file2:
                prompt = txt_file2.read()
            
            # Convertir al formato JSONL
            with open(self.output_jsonl_path, 'w', encoding='utf-8') as jsonl_file:
                for item in data:
                    jsonl_object = {
                        "messages": [
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": item["Q"]},
                            {"role": "assistant", "content": item["A"]}
                        ]
                    }
                    jsonl_file.write(json.dumps(jsonl_object, ensure_ascii=False) + '\n')
            
            print(f"Conversión completada. Archivo JSONL guardado en {self.output_jsonl_path}")
        except Exception as e:
            print(f"Ocurrió un error durante la conversión: {e}")