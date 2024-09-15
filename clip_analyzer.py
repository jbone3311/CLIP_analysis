import os
import logging
import time
import requests
import json
from typing import Dict, Any
from analyzer import Analyzer
from api_utils import retry_with_backoff, log_api_conversation
from image_utils import encode_image_to_base64, generate_unique_code
import json_utils

class CLIPAnalyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config.image_directory)
        self.config = config
        self.logger = logging.getLogger('CLIP_API')

    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def send_clip_request(self, image_base64: str) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        payload = {
            "image": image_base64,
            "model": self.config.clip_model_name,
        }
        
        try:
            response = requests.post(
                f"{self.config.api_base_url}/sdapi/v1/interrogate",
                json=payload, 
                headers=headers, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            response_data = response.json()
            
            log_payload = {**payload, "image": "[BASE64_IMAGE_CONTENT]"}
            log_api_conversation(self.logger, {"request": log_payload, "response": response_data})
            
            return response_data
        except requests.RequestException as e:
            self.logger.error(f"Error in CLIP API request: {str(e)}")
            self.logger.error(f"Response content: {e.response.text if e.response else 'No response content'}")
            raise

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        try:
            image_base64 = encode_image_to_base64(image_path)
            if image_base64 is None:
                raise ValueError(f"Failed to encode image: {image_path}")
            
            results = self.send_clip_request(image_base64)
            
            return {
                'file_info': self._get_file_info(image_path),
                'analysis': results
            }
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {str(e)}")
            return {'error': str(e)}

    def _get_file_info(self, image_path: str) -> Dict[str, Any]:
        return {
            'filename': os.path.basename(image_path),
            'unique_hash': generate_unique_code(image_path),
            'date_created': os.path.getctime(image_path),
            'date_processed': time.time(),
            'file_size': os.path.getsize(image_path)
        }

    def process_images(self):
        existing_files = json_utils.get_existing_json_files(self.config.output_directory)
        for image_path in self.get_image_files():
            if json_utils.should_process_file(image_path, existing_files, self.__class__.__name__, self.config):
                result = self.analyze_image(image_path)
                self.save_result(image_path, result)

    def get_image_files(self):
        for root, _, files in os.walk(self.config.image_directory):
            for file in files:
                if file.lower().endswith(tuple(self.config.image_file_extensions)):
                    yield os.path.join(root, file)

    def save_result(self, image_path: str, result: Dict[str, Any]):
        try:
            json_path = f"{os.path.splitext(image_path)[0]}_{self.__class__.__name__}.json"
            with open(json_path, 'w') as f:
                json.dump(result, f, indent=4)
            logging.info(f"Saved analysis result to {json_path}")
            
            # Process JSON to TXT if enabled
            json_utils.process_json_to_txt(self.config, result, os.path.dirname(json_path))
        except Exception as e:
            logging.error(f"Error saving result to {json_path}: {str(e)}")
