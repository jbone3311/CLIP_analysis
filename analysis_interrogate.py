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
        print(f"✅ Saved output to {filename}")
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
            print(f"❌ Failed to get prompt for mode '{mode}'. Error: {e}")
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
        print(f"❌ Image file '{image_path}' not found.")
        return
    
    results = {
        "image": os.path.abspath(image_path),
        "model": model,
        "prompts": {},
        "analysis": {}
    }
    
    # Generate prompts
    if modes:
        print(f"🔍 Generating prompts for modes: {', '.join(modes)}")
        try:
            prompts = prompt_image(image_path, api_base_url, model, modes)
            results["prompts"] = prompts
        except Exception as e:
            print(f"❌ An error occurred during prompt generation: {e}")
    
    # Perform analysis
    print("📊 Performing image analysis.")
    try:
        analysis = analyze_image(image_path, api_base_url, model)
        results["analysis"] = analysis
    except Exception as e:
        print(f"❌ An error occurred during analysis: {e}")
    
    # Save results to JSON
    try:
        save_json(results, output_filename)
    except Exception as e:
        print(f"❌ Failed to save results: {e}")

if __name__ == "__main__":
    main()
