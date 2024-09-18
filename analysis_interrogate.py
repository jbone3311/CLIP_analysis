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

def analyze_image(image_path: str, enable_clip_analysis: bool, enable_caption: bool,
                  enable_best: bool, enable_fast: bool, enable_classic: bool, enable_negative: bool) -> dict:
    # Placeholder for actual analysis logic based on CLIP settings
    analysis_result = {}
    if enable_clip_analysis:
        analysis_result["clip_analysis"] = "CLIP analysis performed."
    if enable_caption:
        analysis_result["caption"] = "Generated caption for the image."
    if enable_best:
        analysis_result["best"] = "Best analysis results."
    if enable_fast:
        analysis_result["fast"] = "Fast analysis completed."
    if enable_classic:
        analysis_result["classic"] = "Classic analysis mode."
    if enable_negative:
        analysis_result["negative"] = "Negative analysis performed."
    return analysis_result

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

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
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
        '--modes',
        nargs='+',
        choices=['best', 'fast', 'classic', 'negative'],
        help='Specify modes to use for analysis'
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="analysis_results.json",
        help="Filename for the JSON output (default: analysis_results.json)."
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()  # Use the existing argument parser

    config = Config()
    setup_logging(config)

    try:
        if not os.path.isfile(args.image_path):
            raise FileNotFoundError(f"Image file '{args.image_path}' does not exist.")

        analysis_result = analyze_image(
            args.image_path,
            enable_clip_analysis=args.enable_clip_analysis,
            enable_caption=args.enable_caption,
            enable_best=args.enable_best,
            enable_fast=args.enable_fast,
            enable_classic=args.enable_classic,
            enable_negative=args.enable_negative
        )
        filename = os.path.basename(args.image_path)
        
        results = {
            "filename": filename,
            "analysis": analysis_result
        }

        if args.output_to_stdout:
            print(json.dumps(results, indent=4))
        else:
            json_path = os.path.join(config.output_directory, f"{os.path.splitext(filename)[0]}.json")
            with open(json_path, "w") as f:
                json.dump(results, f, indent=4)
            logging.info(f"{config.EMOJI_COMPLETE} Results saved to {json_path}")

    except Exception as e:
        error_result = {"error": str(e)}
        if args.output_to_stdout:
            print(json.dumps(error_result))
        else:
            json_path = os.path.join(config.output_directory, f"{os.path.splitext(filename)[0]}_error.json")
            with open(json_path, "w") as f:
                json.dump(error_result, f, indent=4)
            logging.error(f"{config.EMOJI_ERROR} Failed to process image {args.image_path}: {e}")

if __name__ == "__main__":
    main()
