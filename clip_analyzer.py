import os
import logging
import traceback
from typing import Dict, Any
from dotenv import load_dotenv
from analyzer import Analyzer
from utils import encode_image_to_base64, generate_unique_code
from api_utils import analyze_image_detailed

load_dotenv()

class CLIPAnalyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config.image_directory)
        self.config = config
        self.api_base_url = config.api_base_url
        self.timeout = config.timeout

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        try:
            image_base64 = encode_image_to_base64(image_path)
            unique_code = generate_unique_code(image_path)
            subdir = os.path.basename(os.path.dirname(image_path))
            file = os.path.basename(image_path)
            
            detailed_results = {
                'filename': file,
                'unique_code': unique_code,
                'directory_name': subdir,
                'model': self.config.model,
                'prompts': {},
                'analysis': {}
            }
            
            analysis_result = analyze_image_detailed(image_base64, self.config.model, self.config.caption_types, self.api_base_url, self.timeout, self.config)
            detailed_results['analysis'] = analysis_result
            
            return detailed_results
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

    def process_images(self):
        for image_path in self.get_image_files():
            result = self.analyze_image(image_path)
            # Process the result as needed

def process_clip_images(config) -> None:
    analyzer = CLIPAnalyzer(config)
    analyzer.process_directory()
