###### FILENAME: analysis_LLM.py ######
#!/usr/bin/env python3
"""
LLMAnalyzer Standalone Script

This script analyzes an image or a directory of images using a selected LLM (Language Model) API.
It accepts prompts directly or via prompt IDs defined in a LLM_Prompts.json file,
sends requests to the API, and generates a JSON file with the results.

Usage:
    python analysis_LLM.py <image_path_or_directory> --prompt <prompt1,prompt2,...> --model <model_number> [--output <output_file>] [--debug]

Arguments:
    image_path_or_directory: Path to the image file or directory to be processed.
    --prompt: Comma-separated prompts or prompt IDs (e.g., 'PROMPT1,PROMPT2'). Use 'list' to display all prompts.
    --model: Model number for analysis (1-5) or 'list' to display all models.
    --output: Optional output file path for the JSON results.
    --debug: Enable debug logging.

Example:
    python analysis_LLM.py test.png --prompt "PROMPT1,PROMPT2" --model 2 --output results.json
    python analysis_LLM.py images/ --prompt "PROMPT1,PROMPT2" --model 2 --output results.json

To list all available models:
    python analysis_LLM.py --model list

To list all available prompts:
    python analysis_LLM.py --prompt list
"""

import os
import logging
import requests
import argparse
import json
import base64
import sys
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Load status messages from .env or set default text labels
EMOJI_SUCCESS = os.getenv("EMOJI_SUCCESS", "(SUCCESS)")
EMOJI_WARNING = os.getenv("EMOJI_WARNING", "(WARNING)")
EMOJI_ERROR = os.getenv("EMOJI_ERROR", "(ERROR)")
EMOJI_INFO = os.getenv("EMOJI_INFO", "(INFO)")
EMOJI_PROCESSING = os.getenv("EMOJI_PROCESSING", "(PROCESSING)")
EMOJI_START = os.getenv("EMOJI_START", "(START)")
EMOJI_COMPLETE = os.getenv("EMOJI_COMPLETE", "(COMPLETE)")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Config:
    RETRY_LIMIT = int(os.getenv("RETRY_LIMIT", 5))
    TIMEOUT = int(os.getenv("TIMEOUT", 60))
    LOG_API_CONVERSATION = os.getenv("LOG_API_CONVERSATION", "False").lower() in ("true", "1", "t")

# Load LLM models from .env
def load_llm_models() -> List[Dict[str, str]]:
    """
    Loads all defined LLM models from the .env file.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing LLM model configurations.
    """
    models = []
    model_number = 1
    while True:
        model_title = os.getenv(f"LLM_{model_number}_TITLE")
        model_api_url = os.getenv(f"LLM_{model_number}_API_URL")
        model_api_key = os.getenv(f"LLM_{model_number}_API_KEY")
        model_model = os.getenv(f"LLM_{model_number}_MODEL")
        if not model_title or not model_api_url or not model_model:
            break
        models.append({
            "number": model_number,
            "title": model_title,
            "api_url": model_api_url,
            "api_key": model_api_key,
            "model_name": model_model
        })
        model_number += 1
    return models

MODELS = load_llm_models()

# Load prompt choices from .env
PROMPT_CHOICES = os.getenv("PROMPT_CHOICES", "")

# Load prompts from LLM_Prompts.json
PROMPTS_FILE = 'LLM_Prompts.json'
if not os.path.exists(PROMPTS_FILE):
    # Create a sample LLM_Prompts.json file if it doesn't exist
    sample_prompts = {
        "P1": {
            "TITLE": "Detailed Image Description",
            "PROMPT_TEXT": "Describe the contents of the image...",
            "TEMPERATURE": 0.7,
            "MAX_TOKENS": 3000
        },
        "P2": {
            "TITLE": "Art Critique from Multiple Perspectives",
            "PROMPT_TEXT": "You are an art critic tasked with...",
            "TEMPERATURE": 0.8,
            "MAX_TOKENS": 2000
        }
    }
    with open(PROMPTS_FILE, 'w') as f:
        json.dump(sample_prompts, f, indent=4)

with open(PROMPTS_FILE, 'r') as f:
    PROMPTS = json.load(f)

def retry_request(func):
    """
    Decorator to retry a function call based on RETRY_LIMIT.
    """
    def wrapper(*args, **kwargs):
        retry_limit = Config.RETRY_LIMIT
        for attempt in range(1, retry_limit + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.warning(f"{EMOJI_WARNING} Attempt {attempt} failed with error: {e}")
                if attempt == retry_limit:
                    logging.error(f"{EMOJI_ERROR} All {retry_limit} attempts failed.")
                    raise
                else:
                    logging.info(f"{EMOJI_INFO} Retrying... ({attempt}/{retry_limit})")
                    time.sleep(2)  # Wait before retrying
    return wrapper

class LLMAnalyzer:
    def __init__(self, api_url: str, api_key: str, model_name: str, title: str, debug: bool = False):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.title = title
        self.debug = debug

    @retry_request
    def process_image(self, image_path: str, prompts: List[str], output_file: Optional[str] = None):
        logging.info(f"{EMOJI_PROCESSING} Processing image: {image_path}")
        absolute_image_path = os.path.abspath(image_path)
        
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logging.error(f"{EMOJI_ERROR} Unable to read image file. Error: {e}")
            sys.exit(1)

        results = []
        for prompt in prompts:
            prompt_details = PROMPTS.get(prompt, {})
            prompt_text = prompt_details.get('PROMPT_TEXT', prompt)
            temperature = float(prompt_details.get('TEMPERATURE', 0.7))
            max_tokens = int(prompt_details.get('MAX_TOKENS', 1500))  # Increase the default value
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                        ]
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=Config.TIMEOUT)
                response.raise_for_status()
                logging.info(f"Response from API: {response.json()}")
                results.append({
                    "prompt": prompt,
                    "result": response.json()
                })
            except requests.RequestException as e:
                logging.error(f"{EMOJI_ERROR} Failed to process prompt '{prompt}'. Status code: {getattr(e.response, 'status_code', 'N/A')}")
                logging.error(f"Error details: {str(e)}")
                results.append({
                    "prompt": prompt,
                    "error": str(e)
                })
        
        # Return the results instead of just saving them
        return results

    def save_json(self, data: Dict[str, Any], output_file: str):
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)

def list_models(models: List[Dict[str, Any]]):
    """
    Lists all available models with their information (excluding API keys).

    Args:
        models (List[Dict[str, Any]]): List of model dictionaries.
    """
    print(f"{EMOJI_INFO} Available Models:")
    for model in models:
        print(f"  {EMOJI_INFO} Model {model['number']}: {model['title']}")
        print(f"      API URL: {model['api_url']}")
        print(f"      Model: {model['model_name']}\n")

def list_prompts(prompts: Dict[str, Dict[str, Any]]):
    """
    Lists all available prompts defined in the LLM_Prompts.json file.

    Args:
        prompts (Dict[str, Dict[str, Any]]): Dictionary of prompt IDs and their details.
    """
    if not prompts:
        print(f"{EMOJI_WARNING} No prompts found in the LLM_Prompts.json file.")
        return
    
    print(f"{EMOJI_INFO} Available Prompts:")
    for prompt_id, prompt_details in sorted(prompts.items()):
        first_line = prompt_details['PROMPT_TEXT'].splitlines()[0]
        print(f"  {EMOJI_INFO} {prompt_id}: {prompt_details['TITLE']} - {first_line}... (Temperature: {prompt_details['TEMPERATURE']}, Max Tokens: {prompt_details['MAX_TOKENS']})")

def analyze_image_with_llm(image_path_or_directory: str, prompt_ids: List[str], model_number: int, output_file: str = None, debug: bool = False) -> str:
    try:
        # Configure logging levels
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Validate and retrieve model configuration
        model_config = next((model for model in MODELS if model['number'] == model_number), None)
        if not model_config:
            logging.error(f"Invalid model number: {model_number}.")
            return "ERROR: Analysis Failed"

        # Initialize LLMAnalyzer
        analyzer = LLMAnalyzer(
            api_url=model_config['api_url'],
            api_key=model_config['api_key'],
            model_name=model_config['model_name'],
            title=model_config['title'],
            debug=debug
        )

        # Prepare prompts for analysis
        prompt_details = {prompt_id: PROMPTS[prompt_id] for prompt_id in prompt_ids if prompt_id in PROMPTS}
        prompt_texts = [details['PROMPT_TEXT'] for details in prompt_details.values()]

        # Process the image and get results
        api_responses = analyzer.process_image(image_path_or_directory, prompt_ids, output_file)

        # Collect prompt and model information
        output_data = {
            "model": model_config['model_name'],
            "file_directory": os.path.dirname(image_path_or_directory),
            "file_name": os.path.basename(image_path_or_directory),
            "prompts": prompt_details,
            "api_responses": api_responses  # Use the returned API responses
        }

        # Save or print the output
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=4)
            logging.info(f"Results saved to {output_file}")
        else:
            return json.dumps(output_data, indent=4)

        return "SUCCESS: Analysis Completed"

    except Exception as e:
        logging.error(f"ERROR: Analysis Failed due to {str(e)}")
        return "ERROR: Analysis Failed"

def main():
    parser = argparse.ArgumentParser(description="LLM Analysis")
    parser.add_argument("image_path_or_directory", type=str, help="Path to the image file or directory.")
    parser.add_argument("--prompt", type=str, help="Comma-separated prompt IDs.")
    parser.add_argument("--model", type=int, required=True, help="Model number for analysis.")
    parser.add_argument("--output", type=str, help="Output file path for the JSON results.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    args = parser.parse_args()

    # Use prompt choices from .env if not provided via command line
    prompt_ids = [p.strip() for p in (args.prompt or PROMPT_CHOICES).split(',') if p.strip()]

    result = analyze_image_with_llm(args.image_path_or_directory, prompt_ids, args.model, args.output, args.debug)
    print(result)

if __name__ == "__main__":
    main()