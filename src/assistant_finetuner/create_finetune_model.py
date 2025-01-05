import time
from openai import OpenAI

class OpenAIFineTuner:
    def __init__(self, api_key: str):
        """
        Initialize the OpenAIFineTuner with the API key.
        """
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def create_fine_tuning_job(self, training_file_id: str, model: str, suffix: str = None) -> dict:
        """
        Create a fine-tuning job.

        Args:
            training_file_id (str): The ID of the uploaded training file.
            model (str): The base model to fine-tune.
            suffix (str, optional): A custom suffix for the fine-tuned model name.

        Returns:
            dict: The response from the OpenAI API.
        """
        try:
            response = self.client.fine_tuning.jobs.create(
                training_file=training_file_id,
                model=model,
                suffix=suffix
            )
            print("Fine-tuning job created successfully!")
            return response
        except Exception as e:
            print(f"An error occurred while creating the fine-tuning job: {e}")
            raise

    def monitor_fine_tuning_job(self, fine_tuning_job_id: str):
        """
        Monitor the status of a fine-tuning job until completion.

        Args:
            fine_tuning_job_id (str): The ID of the fine-tuning job.
        """
        print(f"Monitoring fine-tuning job {fine_tuning_job_id}...")
        while True:
            job_status = self.client.fine_tuning.jobs.retrieve(fine_tuning_job_id)
            status = job_status.status
            print(f"Current status: {status}")
            if status in ["succeeded", "failed", "cancelled"]:
                print(f"Fine-tuning job {fine_tuning_job_id} finished with status: {status}")
                model_id = job_status.fine_tuned_model
                return model_id
                break
            time.sleep(30)  # Wait for 30 seconds before checking again

    def list_fine_tuning_jobs(self, limit: int = 10) -> list:
        """
        List fine-tuning jobs.

        Args:
            limit (int): Number of jobs to list.

        Returns:
            list: The fine-tuning jobs.
        """
        try:
            response = self.client.fine_tuning.jobs.list(limit=limit)
            return response.get("data", [])
        except Exception as e:
            print(f"An error occurred while listing fine-tuning jobs: {e}")
            raise

# Example usage:
if __name__ == "__main__":
    api_key = "your_openai_api_key_here"  # Replace with your API key
    tuner = OpenAIFineTuner(api_key)

    # Assuming file upload is complete and you have a file ID
    training_file_id = "file-5QVjv5hCJwc45ZciHP6KBT"  # Replace with the file ID
    model_name = "gpt-4o-mini-2024-07-18"  # Replace with the model name to fine-tune

    # Create a fine-tuning job
    try:
        job_response = tuner.create_fine_tuning_job(training_file_id, model_name, suffix="custom-finetune")
        fine_tuning_job_id = job_response.get("id")
        print("Fine-tuning job response:", job_response)

        # Monitor the job until it finishes
        tuner.monitor_fine_tuning_job(fine_tuning_job_id)
    except Exception as e:
        print(f"Failed to create or monitor fine-tuning job: {e}")
