import os
import logging
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from analyzer import Analyzer
from utils import encode_image_to_base64
from api_utils import log_api_conversation, retry_with_backoff
from json_utils import should_process_file, get_existing_json_files

load_dotenv()

class LLMAnalyzer(Analyzer):
    """
    LLMAnalyzer class for analyzing images using a Language Model API.
    Inherits from the Analyzer base class.
    """

    def __init__(self, config):
        """
        Initialize the LLMAnalyzer.

        Args:
            config: Configuration object containing necessary settings.
        """
        super().__init__(config.image_directory)
        self.config = config
        self.logger = logging.getLogger('LLM_API')

    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def send_llm_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the LLM API.

        Args:
            data (Dict[str, Any]): The data payload for the API request.

        Returns:
            Dict[str, Any]: The API response data.

        Raises:
            requests.RequestException: If the API request fails.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.get_openai_api_key()}"
        }
        
        try:
            response = requests.post(
                self.config.llm_api_base_url,
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            response_data = response.json()
            
            # Log both request and response
            log_api_conversation(self.logger, {"request": data, "response": response_data})
            
            return response_data
        except requests.RequestException as e:
            self.logger.error(f"Error in LLM API request: {str(e)}")
            self.logger.error(f"Response content: {e.response.text if e.response else 'No response content'}")
            raise

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image using the LLM API.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Dict[str, Any]: Analysis results for each prompt, or an error dictionary.
        """
        try:
            image_base64 = encode_image_to_base64(image_path)
            results = {}
            for prompt_id in self.config.selected_prompts:
                data = self._prepare_llm_data(image_base64, prompt_id)
                results[prompt_id] = self.send_llm_request(data)
            return results
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {str(e)}")
            return {'error': str(e)}

    def _prepare_llm_data(self, image_base64: str, prompt_id: str) -> Dict[str, Any]:
        """
        Prepare the data payload for the LLM API request.

        Args:
            image_base64 (str): Base64 encoded image data.
            prompt_id (str): ID of the prompt to use.

        Returns:
            Dict[str, Any]: Prepared data payload for the API request.
        """
        prompt_options = self.config.get_prompt_options(prompt_id)
        return {
            "model": self.config.llm_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_options['PROMPT_TEXT']},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            "temperature": prompt_options['TEMPERATURE'],
            "max_tokens": prompt_options['MAX_TOKENS'],
            "top_p": self.config.top_p,
            "frequency_penalty": self.config.frequency_penalty,
            "presence_penalty": self.config.presence_penalty
        }

    def process_images(self):
        """
        Process all images in the specified directory.
        """
        existing_files = get_existing_json_files(self.config.output_directory)
        for image_path in self.get_image_files():
            if should_process_file(image_path, existing_files, self.__class__.__name__):
                result = self.analyze_image(image_path)
                self.save_result(image_path, result)

