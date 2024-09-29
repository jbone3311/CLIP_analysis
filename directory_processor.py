import os
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from typing import List, Dict, Any
from requests.exceptions import RequestException

import analysis_interrogate
from analysis_LLM import LLMAnalyzer, MODELS, PROMPTS
import image_metadata  # Import the image_metadata module

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("processing.log", encoding='utf-8')
    ]
)

# Define constants for retry mechanism
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 5))  # seconds

class DirectoryProcessor:
    def __init__(self):
        self.config = self.load_config()
        self.llm_analyzers = self.setup_llm_analyzers() if self.config['ENABLE_LLM_ANALYSIS'] else []
        logging.info("DirectoryProcessor initialized with config: %s", self.config)
        logging.debug(f"Imported process_image function: {analysis_interrogate.process_image}")

    def load_config(self) -> Dict[str, Any]:
        # Load configuration from environment variables or a config file
        config = {
            'API_BASE_URL': os.getenv('API_BASE_URL', 'http://localhost:7860'),
            'CLIP_MODEL_NAME': os.getenv('CLIP_MODEL_NAME', 'ViT-L-14/openai'),
            'ENABLE_CLIP_ANALYSIS': os.getenv('ENABLE_CLIP_ANALYSIS', 'True') == 'True',
            'ENABLE_LLM_ANALYSIS': os.getenv('ENABLE_LLM_ANALYSIS', 'True') == 'True',
            'ENABLE_PARALLEL_PROCESSING': os.getenv('ENABLE_PARALLEL_PROCESSING', 'False') == 'True',
            'IMAGE_DIRECTORY': os.getenv('IMAGE_DIRECTORY', 'Images'),
            'OUTPUT_DIRECTORY': os.getenv('OUTPUT_DIRECTORY', 'Output'),
            'CLIP_MODES': os.getenv('CLIP_MODES', 'caption,fast').split(','),
            'USE_JSON': os.getenv('USE_JSON', 'True') == 'True'
        }
        logging.debug(f"Config: {config}")
        return config

    def setup_llm_analyzers(self) -> List[LLMAnalyzer]:
        analyzers = []
        for model in MODELS:
            if model.get('enabled', False):  # Use get() to provide a default value
                analyzer = LLMAnalyzer(
                    api_url=model['api_url'],
                    api_key=model['api_key'],
                    model_name=model['model_name'],
                    title=model['title']
                )
                analyzers.append(analyzer)
                logging.info(f"{model['title']} is enabled for analysis.")
            else:
                logging.info(f"{model['title']} is disabled for analysis.")
        return analyzers

    def process_directory(self):
        image_files = self.find_image_files(self.config['IMAGE_DIRECTORY'])
        logging.debug(f"Found image files: {image_files}")

        if self.config['ENABLE_PARALLEL_PROCESSING']:
            with ThreadPoolExecutor() as executor:
                executor.map(self.process_image, image_files)
        else:
            for image_file in image_files:
                self.process_image(image_file)

    def find_image_files(self, directory: str) -> List[str]:
        image_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_files.append(os.path.join(root, file))
        return image_files

    def process_image(self, image_file: str):
        start_time = time.time()
        try:
            logging.info(f"Processing image: {image_file}")
            absolute_path = os.path.abspath(image_file)
            logging.debug(f"Absolute path: {absolute_path}")
            file_size = os.path.getsize(image_file)
            logging.debug(f"File size of {image_file}: {file_size} bytes")

            # Process image metadata
            metadata = image_metadata.extract_metadata(image_file)
            metadata_output_file = os.path.join(self.config['OUTPUT_DIRECTORY'], os.path.basename(image_file).replace('.', '_DATA.json'))
            self.save_results(metadata, metadata_output_file, result_type='metadata')
            logging.info(f"Saved metadata to {metadata_output_file}")

            # Process image with CLIP
            if self.config['ENABLE_CLIP_ANALYSIS']:
                clip_results = analysis_interrogate.process_image(image_file, self.config['CLIP_MODEL_NAME'], self.config['CLIP_MODES'])
                clip_output_file = os.path.join(self.config['OUTPUT_DIRECTORY'], os.path.basename(image_file).replace('.', '_CLIP.json'))
                self.save_results(clip_results, clip_output_file, result_type='CLIP')
                logging.info(f"CLIP analysis completed successfully for {image_file}")

            # Process image with LLM
            if self.config['ENABLE_LLM_ANALYSIS']:
                for analyzer in self.llm_analyzers:
                    try:
                        prompts = list(PROMPTS.keys())
                        results = analyzer.process_image(image_file, prompts)
                        logging.debug(f"LLM results for {image_file}: {results}")

                        if results and 'choices' in results:
                            llm_data = {
                                **metadata,
                                **results
                            }
                            llm_output_file = os.path.join(self.config['OUTPUT_DIRECTORY'], os.path.basename(image_file).replace('.', '_LLM.json'))
                            self.save_results(llm_data, llm_output_file, result_type='LLM')
                            logging.info(f"LLM analysis completed successfully for {image_file}")
                        else:
                            logging.warning(f"No valid results to save for LLM analysis of {image_file}: {results}")
                    except Exception as e:
                        logging.error(f"Error during LLM analysis for {image_file}: {e}")
        except Exception as e:
            logging.error(f"Failed to process image {image_file}: {e}")
        end_time = time.time()
        logging.info(f"Processing time for {image_file}: {end_time - start_time:.2f} seconds")

    def save_results(self, results: Dict[str, Any], filename: str, result_type: str):
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            logging.debug(f"Saving {result_type} results to {filename} with data: {results}")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4)
            logging.info(f"Saved {result_type} results to {filename}")
        except TypeError as e:
            logging.error(f"TypeError while saving {result_type} results to {filename}: {e}")
            logging.debug(f"Data that caused TypeError: {results}")
        except Exception as e:
            logging.error(f"Failed to save {result_type} results to {filename}: {e}")
            logging.debug(f"Data that caused the error: {results}")

if __name__ == "__main__":
    processor = DirectoryProcessor()
    processor.process_directory()