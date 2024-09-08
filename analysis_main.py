import logging
import time
from dotenv import load_dotenv
from config import Config
from logging_setup import setup_logging
from clip_analyzer import CLIPAnalyzer
from llm_analyzer import LLMAnalyzer
from json_utils import process_existing_json_files
from api_utils import test_api

load_dotenv()

def main():
    try:
        config = Config()
        setup_logging(config)

        logging.info("### Processing New Batch ###")

        api_base_url = config.api_base_url
        timeout = config.timeout

        # Increase timeout and number of attempts
        for attempt in range(5):
            if test_api(api_base_url, timeout * 2):
                logging.info("API is responsive and working.")
                clip_analyzer = CLIPAnalyzer(config)
                clip_analyzer.process_images()
                llm_analyzer = LLMAnalyzer(config)
                llm_analyzer.process_images()
                break
            else:
                logging.warning(f"API at {api_base_url} is not responsive. Attempt {attempt + 1} failed.")
                time.sleep(5)  # Increased delay between attempts
        else:
            logging.error(f"API at {api_base_url} is not responsive after 5 attempts. Skipping image processing.")
            logging.info("Please check that the API is enabled in Automatic1111 settings and the URL is correct.")

        process_existing_json_files(config)

    except Exception as e:
        logging.exception(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()