import os
import logging
import traceback
from typing import Dict, Any
from dotenv import load_dotenv
from analyzer import Analyzer
from utils import encode_image_to_base64, generate_unique_code, safe_api_call
from api_utils import send_llm_request
load_dotenv()

class LLMAnalyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config.image_directory)
        self.config = config

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        try:
            image_base64 = encode_image_to_base64(image_path)
            unique_code = generate_unique_code(image_path)
            subdir = os.path.basename(os.path.dirname(image_path))
            file = os.path.basename(image_path)
            
            llm_results = {}
            for llm_key, llm_config in self.config.llms.items():
                if llm_config['enabled']:
                    for prompt_id in self.config.selected_prompts:
                        data = self._prepare_llm_data(image_base64, prompt_id)
                        response = self.send_llm_request(data, llm_config['api_key'])
                        if response:
                            llm_results[f"{llm_key}_{prompt_id}"] = response['choices'][0]['message']['content']
                        else:
                            logging.warning(f"No response received for {llm_key}, prompt ID {prompt_id}.")
            
            return {
                'filename': file,
                'unique_code': unique_code,
                'directory_name': subdir,
                'llm_results': llm_results
            }
        except FileNotFoundError:
            logging.error(f"Image file not found: {image_path}")
            return {'error': 'File not found'}
        except PermissionError:
            logging.error(f"Permission denied when accessing: {image_path}")
            return {'error': 'Permission denied'}
        except Exception as e:
            logging.error(f"Unexpected error analyzing image {image_path}: {str(e)}")
            logging.debug(f"Traceback: {traceback.format_exc()}")
            return {'error': 'Unexpected error', 'details': str(e)}

    def _prepare_llm_data(self, image_base64: str, prompt_id: str) -> Dict[str, Any]:
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

    @safe_api_call
    def send_llm_request(self, data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        return send_llm_request(data, api_key)

    def process_images(self):
        # Implement the logic to process images here
        for image_path in self.get_image_files():
            result = self.analyze_image(image_path)
            # Process the result as needed

# Remove or comment out the following function
# def process_llm_images(config, api_base_url: str, timeout: int) -> None:
#     analyzer = LLMAnalyzer(config)
#     analyzer.process_directory()
