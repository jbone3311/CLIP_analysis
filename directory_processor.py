import os
import json
import logging
import time
import analysis_interrogate
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from typing import List, Dict, Any
from requests.exceptions import RequestException
from analysis_LLM import LLMAnalyzer, MODELS, PROMPTS
import image_metadata  # Import the image_metadata module

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
# logging.debug(f"Environment variables: {os.environ}")
# Define constants for retry mechanism
MAX_RETRIES = 1
RETRY_DELAY = 1  # seconds

class DirectoryProcessor:
    def __init__(self):
        self.config = self.load_config()
        self.llm_analyzers = self.setup_llm_analyzers() if self.config['ENABLE_LLM_ANALYSIS'] else []
        logging.info("DirectoryProcessor initialized with config: %s", self.config)
        logging.debug(f"Imported process_image function: {analysis_interrogate.process_image}")

    def load_config(self):
        config = {
            'API_BASE_URL': os.getenv('API_BASE_URL'),
            'CLIP_MODEL_NAME': os.getenv('CLIP_MODEL_NAME', 'ViT-L-14'),  # Changed default to match CLI
            'ENABLE_CLIP_ANALYSIS': os.getenv('ENABLE_CLIP_ANALYSIS', 'True').lower() == 'true',
            'ENABLE_LLM_ANALYSIS': os.getenv('ENABLE_LLM_ANALYSIS', 'False').lower() == 'true',
            'ENABLE_PARALLEL_PROCESSING': os.getenv('ENABLE_PARALLEL_PROCESSING', 'True').lower() == 'true',
            'IMAGE_DIRECTORY': os.getenv('IMAGE_DIRECTORY', 'Images'),
            'OUTPUT_DIRECTORY': os.getenv('OUTPUT_DIRECTORY', 'Output'),
            'CLIP_MODES': [
                mode for mode, enabled in {
                    'caption': os.getenv('ENABLE_CAPTION', 'True').lower() == 'true',
                    'best': os.getenv('ENABLE_BEST', 'False').lower() == 'true',
                    'fast': os.getenv('ENABLE_FAST', 'True').lower() == 'true',
                    'classic': os.getenv('ENABLE_CLASSIC', 'False').lower() == 'true',
                    'negative': os.getenv('ENABLE_NEGATIVE', 'False').lower() == 'true'
                }.items() if enabled
            ],
            'USE_JSON': os.getenv('USE_JSON', 'True').lower() == 'true',
        }
        logging.debug(f"Config: {config}")
        return config

    def setup_llm_analyzers(self) -> List[LLMAnalyzer]:
        analyzers = []
        for model in MODELS:
            # Check if the LLM is enabled
            enable_key = f"ENABLE_LLM_{model['number']}"
            if os.getenv(enable_key, 'False').lower() == 'true':
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
        image_files = self.get_image_files()
        for image_file in image_files:
            self.process_image(image_file)

    def process_image(self, image_file: str):
        logging.info(f"Processing image: {image_file}")
        logging.debug(f"Absolute path: {os.path.abspath(image_file)}")
        
        if not os.path.isfile(image_file):
            logging.error(f"Image file does not exist: {image_file}")
            return
        
        file_size = os.path.getsize(image_file)
        logging.debug(f"File size of {image_file}: {file_size} bytes")
        
        if file_size == 0:
            logging.error(f"Image file is empty: {image_file}")
            return
        
        # Process image metadata and save to JSON
        output_directory = self.config['OUTPUT_DIRECTORY']
        image_metadata.process_image_file(image_file, output_directory)
        
        clip_output_file = None
        llm_output_files = []
        
        if self.config['ENABLE_CLIP_ANALYSIS']:
            clip_output_file = os.path.join(
                self.config['OUTPUT_DIRECTORY'],
                f"{os.path.splitext(os.path.basename(image_file))[0]}_CLIP.json"
            )
            if os.path.exists(clip_output_file):
                logging.info(f"CLIP analysis already exists for {image_file}. Skipping.")
            else:
                self.process_clip(image_file, clip_output_file)
        
        if self.config['ENABLE_LLM_ANALYSIS']:
            for analyzer in self.llm_analyzers:
                llm_output_file = os.path.join(
                    self.config['OUTPUT_DIRECTORY'],
                    f"{os.path.splitext(os.path.basename(image_file))[0]}_{analyzer.title}_LLM.json"
                )
                llm_output_files.append(llm_output_file)
                if os.path.exists(llm_output_file):
                    logging.info(f"LLM analysis ({analyzer.title}) already exists for {image_file}. Skipping.")
                else:
                    self.process_llm(image_file, analyzer, llm_output_file)

        if self.config['ENABLE_PARALLEL_PROCESSING'] and not all(os.path.exists(f) for f in [clip_output_file] + llm_output_files):
            with ThreadPoolExecutor() as executor:
                futures = []
                if self.config['ENABLE_CLIP_ANALYSIS'] and not os.path.exists(clip_output_file):
                    futures.append(executor.submit(self.process_clip, image_file, clip_output_file))
                if self.config['ENABLE_LLM_ANALYSIS']:
                    for analyzer, output_file in zip(self.llm_analyzers, llm_output_files):
                        if not os.path.exists(output_file):
                            futures.append(executor.submit(self.process_llm, image_file, analyzer, output_file))
                
                for future in futures:
                    future.result()  # This will raise any exceptions that occurred

    def get_image_files(self) -> List[str]:
        image_files = []
        for root, _, files in os.walk(self.config['IMAGE_DIRECTORY']):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_path = os.path.join(root, file)
                    image_files.append(full_path)
                    logging.debug(f"Found image file: {full_path}")  # Log found image files
        return image_files

    def process_clip(self, image_file: str, output_file: str):
        try:
            logging.info(f"Attempting CLIP analysis for {image_file}")
            
            # Check if analysis already exists
            if os.path.isfile(output_file):
                logging.info(f"CLIP analysis already exists for {image_file}. Skipping.")
                return
            
            results = analysis_interrogate.process_image(
                image_file,
                self.config['API_BASE_URL'],
                self.config['CLIP_MODEL_NAME'],
                self.config['CLIP_MODES']
            )
            
            logging.debug(f"Received results: {results}")
            
            # Check if results contain errors
            if 'error' in results:
                logging.error(f"CLIP analysis failed for {image_file}: {results['error']}")
                return  # Do not save results if there was an error
            
            # Save results if valid
            if self.config['USE_JSON'] and results and results.get('prompts') and results.get('analysis'):
                self.save_results(results, output_file)
                logging.info(f"CLIP analysis completed successfully for {image_file}")
            else:
                logging.warning(f"No valid results to save for {image_file}")
        except Exception as e:
            logging.error(f"Error in CLIP analysis for {image_file}: {e}")
            # Do not save results if an error occurred

    def process_llm(self, image_file: str, analyzer: LLMAnalyzer, output_file: str):
        try:
            logging.info(f"Starting LLM analysis for {image_file} with {analyzer.title}")
            prompts = list(PROMPTS.keys())  # Use all available prompts
            results = analyzer.process_image_for_module(image_file, prompts)
            logging.debug(f"LLM results for {image_file} with {analyzer.title}: {results}")
            
            # Check if there was an error
            if 'error' in results:
                logging.error(f"LLM analysis failed for {image_file} with {analyzer.title}. Not saving results.")
                return  # Do not save JSON if there was an error
            
            if self.config['USE_JSON']:
                self.save_results(results, output_file)
        except Exception as e:
            logging.error(f"Error processing {image_file} with LLM {analyzer.title}: {e}")

    def save_results(self, results: Dict[str, Any], filename: str):
        if results and results.get('prompts') and results.get('analysis'):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(results, f, indent=4)
            logging.info(f"Saved results to {filename}")
        else:
            logging.warning(f"No valid results to save for {filename}")

if __name__ == "__main__":
    processor = DirectoryProcessor()
    processor.process_directory()