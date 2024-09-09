import os
import logging
import requests
import time
from typing import Dict, Any, List, Optional
from analyzer import Analyzer
from api_utils import retry_with_backoff, log_api_conversation
from image_utils import encode_image_to_base64, generate_unique_code, process_image_for_analysis
import json_utils

class CLIPAnalyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger('CLIP_API')

    def _get_enabled_modes(self):
        return [mode for mode, enabled in {
            'caption': self.config.enable_caption,
            'best': self.config.enable_best,
            'fast': self.config.enable_fast,
            'classic': self.config.enable_classic,
            'negative': self.config.enable_negative
        }.items() if enabled]

    @retry_with_backoff(max_retries=3, backoff_factor=2)
    def send_clip_request(self, image_base64: str, mode: str) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        payload = {
            "image": image_base64,
            "model": self.config.clip_model_name,
            "mode": mode
        }
        
        try:
            response = requests.post(
                f"{self.config.api_base_url}/interrogator/prompt", 
                json=payload, 
                headers=headers, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            response_data = response.json()
            
            log_payload = {**payload, "image": "[BASE64_IMAGE_CONTENT]"}
            log_api_conversation(self.logger, {"request": log_payload, "response": response_data})
            
            return {
                'result': response_data,
                'model': self.config.clip_model_name,
                'mode': mode
            }
        except requests.RequestException as e:
            self.logger.error(f"Error in CLIP API request (mode: {mode}): {str(e)}")
            self.logger.error(f"Response content: {e.response.text if e.response else 'No response content'}")
            raise

    def analyze_image(self, image_path: str, modes: List[str]) -> Optional[Dict[str, Any]]:
        try:
            image_base64 = process_image_for_analysis(image_path)
            if image_base64 is None:
                raise ValueError(f"Failed to process image: {image_path}")
            
            results = {}
            for mode in modes:
                logging.info(f"Analyzing image {os.path.basename(image_path)} with mode: {mode}")
                try:
                    results[mode] = self.send_clip_request(image_base64, mode)
                except Exception as e:
                    logging.error(f"Error in mode {mode} for image {image_path}: {str(e)}")
                    return None  # Return None if any mode fails
            
            return {
                'file_info': self._get_file_info(image_path),
                'analysis': results
            }
        except Exception as e:
            logging.error(f"Error analyzing image {image_path}: {str(e)}")
            return None

    def _get_file_info(self, image_path: str) -> Dict[str, Any]:
        try:
            return {
                'filename': os.path.basename(image_path),
                'unique_hash': generate_unique_code(image_path),
                'date_created': os.path.getctime(image_path),
                'date_processed': time.time(),
                'file_size': os.path.getsize(image_path)
            }
        except Exception as e:
            self.logger.error(f"Error getting file info for {image_path}: {str(e)}")
            return {
                'filename': os.path.basename(image_path),
                'error': str(e)
            }

    def get_image_files(self):
        for root, _, files in os.walk(self.config.image_directory):
            for file in files:
                if file.lower().endswith(tuple(self.config.image_file_extensions)):
                    yield os.path.join(root, file)

    def process_images(self):
        for image_path in self.get_image_files():
            logging.info(f"Attempting to analyze image: {image_path}")
            try:
                result = self.analyze_image(image_path, self.enabled_modes)
                if result is not None:
                    json_path = os.path.splitext(image_path)[0] + f"_{self.__class__.__name__}.json"
                    self.save_result(json_path, result)
            except Exception as e:
                logging.error(f"Error processing image {image_path}: {str(e)}")
                # Do not create any error files, just log the error

    def save_result(self, json_path: str, result: Dict[str, Any]):
        try:
            with open(json_path, 'w') as f:
                json.dump(result, f, indent=4)
            logging.info(f"Saved analysis result to {json_path}")
        except Exception as e:
            logging.error(f"Error saving result to {json_path}: {str(e)}")
