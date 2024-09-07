import logging
import time
from config import Config
from utils.logging_setup import setup_logging
from analysis.clip_analysis import process_clip_images
from analysis.llm_analysis import process_llm_images
from utils.json_utils import process_existing_json_files
from utils.api_utils import test_api

def main():
    """
    Main function to run the analysis.
    """
    config = Config()
    setup_logging(config)

    logging.info("### Processing New Batch ###")

    # Verify the API before starting the image processing
    api_base_url = config.api_base_url
    timeout = config.timeout

    for attempt in range(3):
        if test_api(api_base_url, timeout):
            logging.info("API is responsive and working.")
            process_clip_images(config, api_base_url, timeout)
            process_llm_images(config, api_base_url, timeout)
            break
        else:
            logging.warning("API at %s is not responsive. Attempt %d failed.", api_base_url, attempt + 1)
            time.sleep(2 ** attempt)  # Exponential backoff
    else:
        logging.error("API at %s is not responsive after 3 attempts. Skipping.", api_base_url)

    # Process existing JSON files to generate prompt lists
    process_existing_json_files(config)

if __name__ == "__main__":
    main()