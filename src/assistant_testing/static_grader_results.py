import sys
sys.stdout.reconfigure(encoding='utf-8')  # Aseguramos salida UTF-8

import os
import csv
import re
from tqdm import tqdm
from typing_extensions import override

# Si usas la librería openai (u otra similar), ajústala según tu setup:
from dotenv import load_dotenv
from openai import OpenAI, AssistantEventHandler

class MyEventHandler(AssistantEventHandler):
    """
    Manejador de eventos para capturar (o silenciar) el streaming de respuestas
    del asistente en tiempo real. Puedes personalizarlo según tus necesidades.
    """
    
    @override
    def on_text_created(self, text) -> None:
        # Aquí podrías imprimir algo o procesar el texto inicial
        pass

    @override
    def on_text_delta(self, delta, snapshot):
        # Aquí se reciben fragmentos de la respuesta en tiempo real
        # Por ahora, se deja en blanco o se hace un 'pass'
        pass

    @override
    def on_tool_call_created(self, tool_call):
        # Si el asistente llama a alguna 'tool', podrías manejarlo aquí
        pass

    @override
    def on_tool_call_delta(self, delta, snapshot):
        # Si hay comunicación adicional en tiempo real, puedes capturarla aquí
        pass


class RowProcessor:
    """
    Esta clase procesa una fila a la vez. Construye el prompt a partir de los campos:
      - pregunta
      - respuesta humana
      - respuesta de la máquina
    Luego, llama al asistente con dicho prompt y retorna la respuesta.
    """
    def __init__(self, openai_api_key: str, assistant_id: str):
        """
        :param openai_api_key: La API key de OpenAI (o la que corresponda).
        :param assistant_id: El ID del asistente al que se le enviará el prompt.
        """
        self.openai_api_key = openai_api_key
        self.assistant_id = assistant_id

        # Inicializamos el cliente (ajusta si tu setup es diferente)
        self.client = OpenAI(api_key=self.openai_api_key)

    def build_prompt(self, question: str, human_answer: str, machine_answer: str) -> str:
        """
        Construye el mensaje final que se va a enviar al asistente.
        """
        prompt = (
            f"Pregunta: {question}\n\n"
            f"Respuesta humana: {human_answer}\n\n"
            f"Respuesta asistente: {machine_answer}\n\n"
        )
        return prompt

    def get_assistant_response(self, question: str, human_answer: str, machine_answer: str) -> str:
        """
        Crea un prompt a partir de la fila y obtiene la respuesta del asistente.
        Retorna la respuesta como string.
        """
        prompt = self.build_prompt(question, human_answer, machine_answer)

        try:
            # Creamos un 'thread' o conversación nueva
            thread = self.client.beta.threads.create()

            # Mensaje del usuario
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )

            # Iniciamos el streaming de la respuesta
            with self.client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=self.assistant_id,
                event_handler=MyEventHandler()
            ) as stream:
                stream.until_done()

            # Recuperamos todos los mensajes del hilo
            response_message = self.client.beta.threads.messages.list(thread_id=thread.id)
            if response_message and response_message.data:
                # Filtramos los mensajes del asistente
                assistant_responses = [
                    msg.content for msg in response_message.data if msg.role == 'assistant'
                ]
                if assistant_responses:
                    return assistant_responses[-1]  # Tomamos la última respuesta
                else:
                    return "No hubo respuesta del asistente."
            else:
                return "No hubo respuesta del asistente."

        except Exception as e:
            return f"Error al procesar la fila: {e}"
        

class ResponseCleaner:
    """
    Clase encargada de limpiar la respuesta del asistente.
    Si la respuesta es una lista o no es un string, se convierte en un string.
    Luego, por ejemplo, busca el patrón value='...'.
    """
    def clean(self, assistant_response):
        # 1) Forzamos la respuesta a ser string:
        if isinstance(assistant_response, list):
            # Si es una lista, la convertimos en un solo string
            # (ajusta la forma de unir si lo necesitas)
            assistant_response = " ".join(str(item) for item in assistant_response)
        elif assistant_response is None:
            # Si es None, ponemos vacío
            assistant_response = ""
        else:
            # Aseguramos que sea string por si es otro tipo
            assistant_response = str(assistant_response)

        # 2) Aplicas la lógica que tenías, por ejemplo extraer el value='...'
        pattern = r"value='([^']*)'"
        match = re.search(pattern, assistant_response)
        if match:
            return match.group(1).strip()
        else:
            # Si no cumple el patrón, devuelves la respuesta tal cual
            return assistant_response
        

class FileManagerGrader:
    """
    Se encarga de:
      1. Leer el CSV de entrada.
      2. Para cada fila, usar RowProcessor -> obtener la respuesta cruda.
      3. Pasar la respuesta por ResponseCleaner -> obtener la parte relevante.
      4. Guardar un CSV con UNA SOLA columna: "grade".
    """
    def __init__(self, openai_api_key: str, assistant_id: str, csv_input_path: str):
        """
        :param openai_api_key: API key de OpenAI
        :param assistant_id: ID del asistente
        :param csv_input_path: Ruta al archivo CSV de entrada
        """
        self.openai_api_key = openai_api_key
        self.assistant_id = assistant_id
        self.csv_input_path = csv_input_path

        self.row_processor = RowProcessor(openai_api_key, assistant_id)
        self.response_cleaner = ResponseCleaner()

    def run(
        self,
        question_column: str,
        human_answer_column: str,
        machine_answer_column: str,
        output_csv_path: str
    ):
        """
        Lee el CSV de entrada, obtiene la respuesta del asistente (1 fila a la vez),
        la limpia y guarda un CSV con solo una columna: "grade".

        :param question_column: nombre de la columna con la pregunta
        :param human_answer_column: nombre de la columna con la respuesta humana
        :param machine_answer_column: nombre de la columna con la respuesta de la máquina
        :param output_csv_path: ruta del archivo de salida
        """
        if not os.path.exists(self.csv_input_path):
            print(f"El archivo {self.csv_input_path} no existe.")
            return

        # Leemos el CSV de entrada
        rows = []
        with open(self.csv_input_path, 'r', encoding='utf-8') as f_in:
            reader = csv.DictReader(f_in)
            for row in reader:
                rows.append(row)

        if not rows:
            print("No se encontraron filas en el CSV de entrada.")
            return

        # Definimos que el CSV de salida solo tendrá una columna: "grade"
        fieldnames = ["grade"]

        # Procesamos filas, generamos la respuesta y la limpiamos
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for row in tqdm(rows, desc="Procesando filas"):
                question = row.get(question_column, "").strip()
                human_answer = row.get(human_answer_column, "").strip()
                machine_answer = row.get(machine_answer_column, "").strip()

                # Llamada al asistente
                raw_response = self.row_processor.get_assistant_response(
                    question=question,
                    human_answer=human_answer,
                    machine_answer=machine_answer
                )

                # Limpieza de la respuesta
                clean_response = self.response_cleaner.clean(raw_response)

                # Escribimos SÓLO la columna "grade"
                writer.writerow({"grade": clean_response})

        print(f"\n¡Proceso finalizado! El archivo con resultados se guardó en: {output_csv_path}")



# Ejemplo de uso (ejecutar solo si deseas probar esta clase directamente):
if __name__ == "__main__":
    # Supongamos que en tu .env o tu config ya tienes la API Key y el ID de tu asistente
    openai_api_key = "TU_API_KEY"
    assistant_id = "ID_DE_TU_ASISTENTE"
    input_csv = "ruta_de_tu_archivo_entrada.csv"
    output_csv = "ruta_de_tu_archivo_salida.csv"

    manager = FileManagerGrader(
        openai_api_key=openai_api_key,
        assistant_id=assistant_id,
        csv_input_path=input_csv
    )

    manager.run(
        question_column="pregunta",
        human_answer_column="respuesta_humana",
        machine_answer_column="respuesta_maquina",
        output_csv_path=output_csv  # Aquí indicamos el archivo de salida
    )
