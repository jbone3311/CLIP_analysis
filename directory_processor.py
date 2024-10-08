import os
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from typing import List, Dict, Any
from requests.exceptions import RequestException
from PIL import Image

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
    def __init__(self, config):
        self.config = config
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
            enabled = os.getenv(f"ENABLE_LLM_{model['number']}", 'False').lower() == 'true'
            if enabled:
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
                executor.map(lambda image_file: self.process_image(image_file, self.config['CLIP_MODES']), image_files)
        else:
            for image_file in image_files:
                self.process_image(image_file, self.config['CLIP_MODES'])

    def find_image_files(self, directory: str) -> List[str]:
        image_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_files.append(os.path.join(root, file))
        return image_files

    def process_image(self, image_file: str, modes: List[str]):
        start_time = time.time()
        try:
            logging.info(f"Processing image: {image_file}")
            absolute_image_path = os.path.abspath(image_file)
            logging.debug(f"Absolute path: {absolute_image_path}")

            # Define the output paths for the metadata JSON files
            metadata_output_path = os.path.join(self.config['OUTPUT_DIRECTORY'], f"{os.path.splitext(os.path.basename(image_file))[0]}_DATA.json")
            llm_output_path = os.path.join(self.config['OUTPUT_DIRECTORY'], f"{os.path.splitext(os.path.basename(image_file))[0]}_LLM.json")
            clip_output_path = os.path.join(self.config['OUTPUT_DIRECTORY'], f"{os.path.splitext(os.path.basename(image_file))[0]}_CLIP.json")

            # Skip processing if the JSON files already exist
            if os.path.exists(metadata_output_path) and os.path.exists(llm_output_path) and os.path.exists(clip_output_path):
                logging.info(f"Skipping {image_file} as all output files already exist.")
                return

            # Process metadata
            metadata = image_metadata.extract_metadata(absolute_image_path)

            # Process LLM analysis
            llm_results = None
            if self.config['ENABLE_LLM_ANALYSIS']:
                for analyzer in self.llm_analyzers:
                    logging.info(f"Running LLM analysis with {analyzer.model_name}")
                    llm_results = analyzer.process_image(absolute_image_path, self.config['CLIP_MODES'])
                    logging.debug(f"LLM results: {llm_results}")

            # Process CLIP analysis
            clip_results = None
            if self.config['ENABLE_CLIP_ANALYSIS']:
                clip_results = analysis_interrogate.process_image(absolute_image_path, self.config['API_BASE_URL'], self.config['CLIP_MODEL_NAME'], modes)

            # Save results
            if metadata:
                with open(metadata_output_path, 'w') as f:
                    json.dump(metadata, f, indent=4)
                logging.info(f"Saved metadata results to {metadata_output_path}")

            if llm_results:
                with open(llm_output_path, 'w') as f:
                    json.dump(llm_results, f, indent=4)
                logging.info(f"Saved LLM results to {llm_output_path}")

            if clip_results:
                with open(clip_output_path, 'w') as f:
                    json.dump(clip_results, f, indent=4)
                logging.info(f"Saved CLIP results to {clip_output_path}")

        except Exception as e:
            logging.error(f"Failed to process image {image_file}: {e}")
        finally:
            end_time = time.time()
            logging.info(f"Processing time for {image_file}: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    # Load configuration
    config = {
        'API_BASE_URL': 'http://localhost:7860',
        'CLIP_MODEL_NAME': 'ViT-L-14/openai',
        'ENABLE_CLIP_ANALYSIS': True,
        'ENABLE_LLM_ANALYSIS': True,
        'ENABLE_PARALLEL_PROCESSING': False,
        'IMAGE_DIRECTORY': 'Images',
        'OUTPUT_DIRECTORY': 'Output',
        'CLIP_MODES': ['caption', 'fast'],
        'USE_JSON': True
    }

    processor = DirectoryProcessor(config)
    processor.process_directory()