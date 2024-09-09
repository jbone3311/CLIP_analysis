import logging
import os
from config import Config
from clip_analyzer import CLIPAnalyzer
from llm_analyzer import LLMAnalyzer
import json_utils

def setup_logging(config):
    log_file = os.path.join(config.output_directory, 'analysis.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='a'
    )
    # Also output to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def main():
    config = Config()
    setup_logging(config)

    logging.info("### Processing New Batch ###")

    if config.clip_enabled:
        logging.info("Running CLIP Analyzer...")
        clip_analyzer = CLIPAnalyzer(config)
        clip_analyzer.process_images()

    if config.llm_enabled:
        logging.info("Running LLM Analyzer...")
        llm_analyzer = LLMAnalyzer(config)
        llm_analyzer.process_images()

    logging.info("Finished processing")

if __name__ == "__main__":
    main()