import logging
from dotenv import load_dotenv
from config import Config
from logging_setup import setup_logging
from clip_analyzer import CLIPAnalyzer
from llm_analyzer import LLMAnalyzer
from json_utils import save_json, get_existing_json_files, process_existing_json_files, is_valid_llm_json, should_process_file

load_dotenv()

def main():
    try:
        config = Config()
        setup_logging(config)

        logging.info("### Processing New Batch ###")

        if config.enable_clip_analysis:
            logging.info("Running CLIP Analyzer...")
            clip_analyzer = CLIPAnalyzer(config)
            clip_analyzer.process_images()

        if config.enable_llm_analysis:
            logging.info("Running LLM Analyzer...")
            llm_analyzer = LLMAnalyzer(config)
            llm_analyzer.process_images()

        if config.enable_json_processing:
            logging.info("Processing existing JSON files...")
            process_existing_json_files(config)

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()