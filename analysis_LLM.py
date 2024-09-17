"""
LLMAnalyzer Class

This class is responsible for analyzing images using a selected LLM (Language Model) API. 
It allows for the submission of prompts either directly or by referencing predefined prompts 
from the environment configuration.

Parameters:
    image_path (str): (Required) Path to the image file.
    --prompt (str): The prompt to be used for analysis. You can specify direct prompts or 
                    use prompt IDs (e.g., P1, P2) defined in the .env file.
                    Example: "How many dogs, P1, P2"
    --model (int): Model number for analysis. Choose from available LLMs (1-5).
    --api_base_url (str): Base URL of the LLM API. Default is http://localhost:8000.
    --api_key (str): API key for authentication with the LLM API.
    --title (str): Title for the LLM request.

Example Usage:
    python llm_analyzer.py test.png --prompt "Describe the image." --model 1 --api_base_url http://localhost:8000 --api_key YOUR_API_KEY

In the above example, the script will analyze the image located at 'test.png' using the 
prompt "Describe the image." with the LLM model specified by model number 1.

You can also combine direct prompts with prompt IDs:
    python llm_analyzer.py test.png --prompt "How many dogs, P1, P2" --model 1 --api_base_url http://localhost:8000 --api_key YOUR_API_KEY

In this case, the LLM will process the direct prompt "How many dogs" along with the prompts 
defined in the .env file for P1 and P2.

"""

import os
import logging
import requests
from typing import Optional, Dict, Any, List
from analyzer import Analyzer
from api_utils import retry_with_backoff, log_api_conversation
from image_utils import encode_image_to_base64
import json_utils

class LLMAnalyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config.image_directory)
        self.config = config
        self.logger = logging.getLogger('LLM_API')

    def get_llm_config(self, model_number: int) -> Optional[Dict[str, str]]:
        """Retrieve LLM configuration based on the model number."""
        llm_config = self.config.llm_configs.get(model_number)
        if not llm_config:
            self.logger.error(f"Invalid model number: {model_number}")
            return None
        return llm_config

    def get_prompt_text(self, prompt_id: str) -> str:
        """Retrieve prompt text based on the prompt ID."""
        if prompt_id.startswith('P'):
            index = int(prompt_id[1:])  # Extract the number from 'P1', 'P2', etc.
            prompt_text = os.getenv(f'PROMPT{index}_PROMPT_TEXT')
            return prompt_text if prompt_text else ""
        return prompt_id  # Return the direct prompt if not an ID

    def parse_prompts(self, prompt_input: str) -> List[str]:
        """Parse the input to handle both direct prompts and prompt IDs."""
        prompts = prompt_input.split(',')
        return [self.get_prompt_text(p.strip()) for p in prompts]

    @retry_with_backoff(max_retries=5, initial_wait=1, backoff_factor=2)
    def send_llm_request(self, prompt: str, model_number: int) -> Optional[Dict[str, Any]]:
        llm_config = self.get_llm_config(model_number)
        if not llm_config:
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm_config['api_key']}"
        }
        payload = {
            "prompt": prompt,
            "model": llm_config['model'],
        }

        try:
            log_payload = {**payload, "prompt": "[PROMPT_CONTENT]"}
            self.logger.debug(f"Sending LLM request with payload: {log_payload}")

            response = requests.post(
                f"{llm_config['api_url']}/llm",
                json=payload,
                headers=headers,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            response_data = response.json()
            return response_data
        except requests.HTTPError as e:
            self.logger.error(f"HTTP error occurred during LLM request: {e}")
            self.logger.error(f"Response content: {e.response.text if e.response else 'No response content'}")
            return None
        except requests.RequestException as e:
            self.logger.error(f"Error in LLM API request: {str(e)}")
            return None

    def process_images(self, image_path: str, prompt_input: str, model_number: int):
        existing_files = json_utils.get_existing_json_files(self.config.output_directory)
        if json_utils.should_process_file(image_path, existing_files, self.__class__.__name__, self.config):
            parsed_prompts = self.parse_prompts(prompt_input)  # Parse the prompts
            for prompt in parsed_prompts:
                result = self.send_llm_request(prompt, model_number)
                if result is not None:
                    self.save_result(image_path, result)
                else:
                    self.logger.warning(f"Skipping JSON creation for {image_path} due to LLM request error")

    def create_prompt(self, image_path: str, mode: str) -> str:
        # Create a prompt based on the image and mode
        return f"Analyze the image {image_path} in {mode} mode."

    def get_image_files(self):
        for root, _, files in os.walk(self.config.image_directory):
            for file in files:
                if file.lower().endswith(tuple(self.config.image_file_extensions)):
                    yield os.path.join(root, file)

