import os
import sys
import json
import logging
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from config import Config
from utils.image_utils import encode_image_to_base64
from utils.json_utils import save_json, get_existing_json_files
from utils.api_utils import send_llm_request
from constants import DEFAULTS
from analysis.llm_analysis import process_llm_images

# Test configuration variables
TEST_IMAGE_DIRECTORY = 'test_images'
TEST_SUBDIR = 'test_subdir'
TEST_IMAGE_PATH = r"C:\Users\jiml\Dropbox\#AIArt\SourceCode\CODE_CLIP_Analysis\Images\2\RANDOS (20).png"
REAL_IMAGE_DIRECTORY = 'real_images'  # Placeholder for the real directory path

class TestProcessLLMImages(unittest.TestCase):

    def test_process_llm_images(self):
        # Fetch the API key from the environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.fail("Environment variable 'OPENAI_API_KEY' is not set.")

        # Set up a test configuration
        config = Config()
        config.image_directory = TEST_IMAGE_DIRECTORY
        config.llms = {
            'LLM_1': {
                'enabled': True,
                'api_url': 'https://api.openai.com/v1/chat/completions',
                'api_key': api_key
            }
        }
        config.selected_prompts = ['1']

        # Create test image directory and files
        os.makedirs(os.path.join(TEST_IMAGE_DIRECTORY, TEST_SUBDIR, 'json'), exist_ok=True)
        with open(os.path.join(TEST_IMAGE_DIRECTORY, TEST_SUBDIR, 'test_image.png'), 'wb') as f:
            f.write(open(TEST_IMAGE_PATH, 'rb').read())

        # Run the function
        failed_images = process_llm_images(config, 'https://api.openai.com/v1/chat/completions', 30)

        # Check results
        self.assertFalse(failed_images, "There should be no failed images")

        # Clean up
        os.remove(os.path.join(TEST_IMAGE_DIRECTORY, TEST_SUBDIR, 'test_image.png'))
        os.rmdir(os.path.join(TEST_IMAGE_DIRECTORY, TEST_SUBDIR, 'json'))
        os.rmdir(os.path.join(TEST_IMAGE_DIRECTORY, TEST_SUBDIR))
        os.rmdir(TEST_IMAGE_DIRECTORY)

def real_api_test():
    # Fetch the API key from the environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logging.error("Environment variable 'OPENAI_API_KEY' is not set.")
        return

    # Ensure the real image directory exists
    if not os.path.exists(REAL_IMAGE_DIRECTORY):
        logging.error(f"Directory '{REAL_IMAGE_DIRECTORY}' does not exist.")
        return

    # Set up a real configuration
    config = Config()
    config.image_directory = REAL_IMAGE_DIRECTORY
    config.llms = {
        'LLM_1': {
            'enabled': True,
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key': api_key
        }
    }
    config.selected_prompts = ['1']

    # Run the function with real data
    failed_images = process_llm_images(config, 'https://api.openai.com/v1/chat/completions', 30)

    if not failed_images:
        logging.info("Real API test completed successfully without errors.")
    else:
        logging.error(f"Real API test failed for the following images: {failed_images}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # Uncomment the following line to run the real API test
    real_api_test()