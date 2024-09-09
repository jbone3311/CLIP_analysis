import os
import logging
import requests
from typing import Dict, Any, List
from analyzer import Analyzer
from api_utils import retry_with_backoff, log_api_conversation
from image_utils import encode_image_to_base64
import json_utils

class LLMAnalyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger('LLM_API')

    def _get_enabled_modes(self):
        return self.config.selected_prompts

    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def send_llm_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.get_openai_api_key()}"
        }
        
        # Log the request payload (be careful not to log sensitive information)
        logging.info(f"Sending request to OpenAI API with payload: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(
                self.config.llm_api_base_url,
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            response_data = response.json()
            
            log_api_conversation(self.logger, {"request": data, "response": response_data})
            
            return response_data
        except requests.RequestException as e:
            self.logger.error(f"Error in LLM API request: {str(e)}")
            self.logger.error(f"Response content: {e.response.text if e.response else 'No response content'}")
            raise

    def analyze_image(self, image_path: str, modes: List[str]) -> Dict[str, Any]:
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
            for prompt_id in modes:
                data = self._prepare_llm_data(image_base64, prompt_id)
                results[prompt_id] = self.send_llm_request(data)
            return {
                'file_info': self._get_file_info(image_path),
                'analysis': results
            }
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {str(e)}")
            return {
                'file_info': self._get_file_info(image_path),
                'analysis': {'error': str(e)}
            }

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

