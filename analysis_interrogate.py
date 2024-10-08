import requests
import base64
import os
import json
import argparse
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

# Load status messages from .env or set default words
EMOJI_SUCCESS = os.getenv("EMOJI_SUCCESS", "SUCCESS")
EMOJI_WARNING = os.getenv("EMOJI_WARNING", "WARNING")
EMOJI_ERROR = os.getenv("EMOJI_ERROR", "ERROR")
EMOJI_INFO = os.getenv("EMOJI_INFO", "INFO")
EMOJI_PROCESSING = os.getenv("EMOJI_PROCESSING", "PROCESSING")

def encode_image_to_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            logging.debug(f"Read {len(image_data)} bytes from {image_path}")
            encoded_string = base64.b64encode(image_data).decode("utf-8")
            logging.debug(f"Encoded image (first 100 chars): {encoded_string[:100]}")
            return encoded_string
    except Exception as e:
        logging.error(f"Error encoding image {image_path}: {e}")
        raise FileNotFoundError(f"Unable to encode image. Error: {e}")

def prompt_image(image_path: str, api_base_url: str, model: str, modes: List[str], timeout: int = 60) -> Dict[str, Any]:
    image_base64 = encode_image_to_base64(image_path)
    if not image_base64:
        logging.error(f"Encoded string is empty for image: {image_path}")
        return {"error": "Encoded image is empty"}
    prompts = {}
    headers = {"Content-Type": "application/json"}
    for mode in modes:
        payload = {
            "image": image_base64,
            "model": model,
            "mode": mode
        }
        logging.debug(f"Sending request to {api_base_url}/interrogator/prompt with payload: {json.dumps(payload)[:1000]} and headers: {headers}")
        try:
            response = requests.post(
                f"{api_base_url}/interrogator/prompt",
                json=payload,
                headers=headers,
                timeout=timeout
            )
            logging.debug(f"Response status code: {response.status_code}")
            logging.debug(f"Response content: {response.text[:1000]}")  # Log first 1000 characters
            response.raise_for_status()
            prompts[mode] = response.json()
        except requests.RequestException as e:
            logging.error(f"{EMOJI_ERROR} Failed to get prompt for mode '{mode}'. Error: {e}")
            prompts[mode] = {"error": str(e)}
    return prompts

def analyze_image(image_path: str, api_base_url: str, model: str, timeout: int = 60) -> Dict[str, Any]:
    image_base64 = encode_image_to_base64(image_path)
    if not image_base64:
        logging.error(f"Encoded string is empty for image: {image_path}")
        return {"error": "Encoded image is empty"}
    payload = {
        "image": image_base64,
        "model": model
    }
    headers = {"Content-Type": "application/json"}
    logging.debug(f"Sending request to {api_base_url}/interrogator/analyze with payload: {json.dumps(payload)[:1000]} and headers: {headers}")
    try:
        response = requests.post(
            f"{api_base_url}/interrogator/analyze",
            json=payload,
            headers=headers,
            timeout=timeout
        )
        logging.debug(f"Response status code: {response.status_code}")
        logging.debug(f"Response content: {response.text[:1000]}")  # Log first 1000 characters
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"{EMOJI_ERROR} Failed to analyze image. Error: {e}")
        return {"error": str(e)}

def process_image_with_clip(image_path: str, api_base_url: str, model: str, modes: List[str], output_file: str = None) -> str:
    try:
        # Perform prompt generation
        prompt_results = prompt_image(image_path, api_base_url, model, modes)

        # Perform image analysis
        analysis_results = analyze_image(image_path, api_base_url, model)

        # Collect all results and metadata
        output_data = {
            "model": model,
            "modes": modes,
            "file_directory": os.path.dirname(image_path),
            "file_name": os.path.basename(image_path),
            "prompt_results": prompt_results,
            "analysis_results": analysis_results
        }

        # Save results to JSON if output_file is specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=4)
            logging.info(f"Saved output to {output_file}")
        else:
            return json.dumps(output_data, indent=4)

        return "SUCCESS: Analysis Completed"

    except Exception as e:
        logging.error(f"ERROR: Analysis Failed due to {str(e)}")
        return "ERROR: Analysis Failed"

def save_json(data: Dict[str, Any], filename: str):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    logging.info(f"{EMOJI_SUCCESS} Saved output to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Process an image using the CLIP API.")
    parser.add_argument("image_path", type=str, help="Path to the image file.")
    parser.add_argument("--api_base_url", type=str, default="http://localhost:7860", help="Base URL of the CLIP API.")
    parser.add_argument("--model", type=str, default="ViT-L-14", help="Model name to use for analysis.")
    parser.add_argument("--modes", type=str, nargs='+', default=["best", "fast"], help="Modes for prompt generation.")
    parser.add_argument("--output", type=str, default="output.json", help="Output JSON file.")
    args = parser.parse_args()

    result = process_image_with_clip(args.image_path, args.api_base_url, args.model, args.modes, args.output)
    print(result)

if __name__ == "__main__":
    main()
else:
    # This ensures process_image is available when the module is imported
    __all__ = ['process_image_with_clip']