"""
Parameters:
    image_path (str): (Required) Path to the image file.
    --api_base_url (str): Base URL of the CLIP API. Default is http://localhost:7860.
    --model (str): Model name for analysis and prompt generation. Default is ViT-L-14.
    --modes (List[str]): Prompt modes to generate. Choose from 'best', 'fast', 'classic', 'negative', 'caption'. Default is all.
    --output (str): Filename for the JSON output. Default is analysis_results.json.

Example:
    python analysis_interrogate.py test.png --modes best fast --output output.json
"""

import requests
import base64
import os
import json
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load status messages from .env or set default words
EMOJI_SUCCESS = os.getenv("EMOJI_SUCCESS", "SUCCESS")
EMOJI_WARNING = os.getenv("EMOJI_WARNING", "WARNING")
EMOJI_ERROR = os.getenv("EMOJI_ERROR", "ERROR")
EMOJI_INFO = os.getenv("EMOJI_INFO", "INFO")
EMOJI_PROCESSING = os.getenv("EMOJI_PROCESSING", "PROCESSING")
EMOJI_START = os.getenv("EMOJI_START", "START")
EMOJI_COMPLETE = os.getenv("EMOJI_COMPLETE", "COMPLETE")

def encode_image_to_base64(image_path: str) -> str:
    """
    Encodes an image file to a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string of the image.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise FileNotFoundError(f"Unable to encode image. Error: {e}")

def save_json(data: Dict[str, Any], filename: str):
    """
    Saves data to a JSON file.

    Args:
        data (dict): The data to save.
        filename (str): The name of the file to save the data to.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"{EMOJI_SUCCESS} Saved output to {filename}")
    except Exception as e:
        raise IOError(f"Failed to save JSON to {filename}. Error: {e}")

def analyze_image(image_path: str, api_base_url: str, model: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Sends an image to the CLIP API for analysis.

    Args:
        image_path (str): The path to the image file.
        api_base_url (str): The base URL of the API.
        model (str): The model name to use for analysis.
        timeout (int): The timeout for the API request (default is 60 seconds).

    Returns:
        dict: The JSON response from the API containing analysis results.
    """
    image_base64 = encode_image_to_base64(image_path)
    
    payload = {
        "image": image_base64,
        "model": model
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(
            f"{api_base_url}/interrogator/analyze",
            json=payload,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise ConnectionError(f"API request failed during analysis. Error: {e}")

def prompt_image(image_path: str, api_base_url: str, model: str, modes: List[str], timeout: int = 60) -> Dict[str, Any]:
    """
    Sends an image to the CLIP API to generate prompts.

    Args:
        image_path (str): The path to the image file.
        api_base_url (str): The base URL of the API.
        model (str): The model name to use for generating prompts.
        modes (List[str]): List of modes for prompt generation (e.g., 'fast', 'best').
        timeout (int): The timeout for the API request (default is 60 seconds).

    Returns:
        dict: The JSON response from the API containing prompt results.
    """
    image_base64 = encode_image_to_base64(image_path)
    prompts = {}

    headers = {"Content-Type": "application/json"}

    for mode in modes:
        payload = {
            "image": image_base64,
            "model": model,
            "mode": mode
        }

        try:
            response = requests.post(
                f"{api_base_url}/interrogator/prompt",
                json=payload,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            prompts[mode] = response.json()
        except requests.RequestException as e:
            print(f"{EMOJI_ERROR} Failed to get prompt for mode '{mode}'. Error: {e}")
            prompts[mode] = {"error": str(e)}
    
    return prompts

def process_image(image_path: str, api_base_url: str, model: str, modes: List[str]) -> Dict[str, Any]:
    results = {
        "image": os.path.abspath(image_path),
        "model": model,
        "prompts": {},
        "analysis": {}
    }
    
    # Generate prompts
    if modes:
        print(f"{EMOJI_PROCESSING} Generating prompts for modes: {', '.join(modes)}")
        try:
            prompts = prompt_image(image_path, api_base_url, model, modes)
            results["prompts"] = prompts
        except Exception as e:
            print(f"{EMOJI_ERROR} An error occurred during prompt generation: {e}")
    
    # Perform analysis
    print(f"{EMOJI_PROCESSING} Performing image analysis.")
    try:
        analysis = analyze_image(image_path, api_base_url, model)
        results["analysis"] = analysis
    except Exception as e:
        print(f"{EMOJI_ERROR} An error occurred during analysis: {e}")
    
    return results

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process images to generate prompts and perform analysis using the CLIP API."
    )
    
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to the image file to be processed."
    )
    
    parser.add_argument(
        "--api_base_url",
        type=str,
        default="http://localhost:7860",
        help="Base URL of the CLIP API (default: http://localhost:7860)."
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default="ViT-L-14",
        help="Model name to use for analysis and prompt generation (default: ViT-L-14)."
    )
    
    parser.add_argument(
        "--modes",
        type=str,
        nargs='+',
        choices=['best', 'fast', 'classic', 'negative', 'caption'],
        default=['best', 'fast', 'classic', 'negative', 'caption'],
        help="Prompt modes to generate. Choose from 'best', 'fast', 'classic', 'negative', 'caption'. Default is all."
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="analysis_results.json",
        help="Filename for the JSON output (default: analysis_results.json)."
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    image_path = args.image_path
    api_base_url = args.api_base_url
    model = args.model
    modes = args.modes
    output_filename = args.output
    
    # Verify that the image file exists
    if not os.path.isfile(image_path):
        print(f"{EMOJI_ERROR} Image file '{image_path}' not found.")
        return
    
    results = process_image(image_path, api_base_url, model, modes)
    
    # Save results to JSON
    try:
        save_json(results, output_filename)
    except Exception as e:
        print(f"{EMOJI_ERROR} Failed to save results: {e}")

if __name__ == "__main__":
    main()
else:
    # This ensures process_image is available when the module is imported
    __all__ = ['process_image']
