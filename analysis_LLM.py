#!/usr/bin/env python3
"""
LLMAnalyzer Standalone Script

This script analyzes an image using a selected LLM (Language Model) API.
It accepts prompts directly or via prompt IDs defined in a LLM_Prompts.json file,
sends requests to the API, and generates a JSON file with the results.

Usage:
    python analysis_LLM.py <image_path> --prompt <prompt> --model <model_number> [--output <output_file>] [--debug]

Arguments:
    image_path: Path to the image file to be processed.
    --prompt: Comma-separated prompts or prompt IDs (e.g., 'Describe the image, P1, P2'). Use 'list' to display all prompts.
    --model: Model number for analysis (1-N) or 'list' to display all models.
    --output: Optional output file path for the JSON results.
    --debug: Enable debug logging.

Example:
    python analysis_LLM.py test.png --prompt "P1" --model 1 --output results.json

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
from typing import Optional, Dict, Any, List
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

# Load models from .env
MODELS = []
model_count = 1
while True:
    model_name = os.getenv(f'LLM_{model_count}_TITLE')
    model_api_url = os.getenv(f'LLM_{model_count}_API_URL')
    model_api_key = os.getenv(f'LLM_{model_count}_API_KEY')
    model_model = os.getenv(f'LLM_{model_count}_MODEL')
    if not model_name or not model_api_url or not model_model:
        break
    MODELS.append({
        'number': model_count,
        'name': model_name,
        'api_url': model_api_url,
        'api_key': model_api_key,
        'model': model_model
    })
    model_count += 1

# Load prompts from LLM_Prompts.json
PROMPTS_FILE = 'LLM_Prompts.json'

if not os.path.exists(PROMPTS_FILE):
    # Create a sample LLM_Prompts.json file if it doesn't exist
    sample_prompts = {
        "PROMPT1": {
            "TITLE": "Detailed Image Description",
            "PROMPT_TEXT": "You will be given an image to describe in detail. Your task is to provide a comprehensive and accurate description of the contents of the image.\n\nFollow these steps to describe the image:\n\n1. Begin by identifying the main subject or focus of the image. What immediately draws your attention?\n\n2. Describe the overall scene or setting. Is it indoors or outdoors? What time of day does it appear to be?\n\n3. Provide details about the main elements in the image, including:\n   - People: Describe their appearance, clothing, actions, and expressions\n   - Objects: Identify and describe key objects, their colors, sizes, and positions\n   - Animals: If present, describe their species, actions, and appearance\n   - Nature: Describe any natural elements like plants, trees, water bodies, or landscapes\n   - Buildings or structures: Describe their architecture, size, and condition\n\n4. Pay attention to colors, lighting, and atmosphere. How do these elements contribute to the overall mood or feel of the image?\n\n5. Describe any text or signage visible in the image.\n\n6. Note any unusual or striking features that stand out.\n\n7. If relevant, describe the composition of the image, including foreground, middle ground, and background elements.\n\n8. If the image depicts an action or event, describe what appears to be happening.\n\nProvide your description in clear, concise language. Be as objective as possible, focusing on what you can actually see rather than making assumptions or interpretations.\n\nIf any part of the image is unclear or difficult to discern, mention this in your description.\n\nIf for any reason you are unable to process or analyze the image, please state this clearly and explain why (e.g., \"I'm sorry, but I am unable to view or analyze the image provided.\").\n\nPresent your final description in detail so a blind person can see the image and an artist can paint it.",
            "TEMPERATURE": 0.7,
            "MAX_TOKENS": 1000
        },
        "PROMPT2": {
            "TITLE": "Art Critique from Multiple Perspectives",
            "PROMPT_TEXT": "You are an art critic tasked with providing a comprehensive critique of an image from multiple perspectives. Your goal is to analyze the image visually, interpret its meaning, and describe how it appears and what it inspires from different viewpoints.\n\nExamine the image carefully and provide a critique from each of the following perspectives:\n\n1. Artist\n2. Gallery owner\n3. Curator\n4. 12-year-old\n5. 19-year-old\n6. 50-year-old\n\nFor each perspective, consider the following aspects:\n- Visual elements (composition, color, style, technique)\n- Emotional impact\n- Potential meaning or symbolism\n- How it relates to current trends or historical context (if applicable)\n- Personal interpretation based on the specific perspective\n\nStructure your response as follows:\n\n<critique>\n<artist_perspective>\n[Provide the artist's critique here]\n</artist_perspective>\n\n<gallery_owner_perspective>\n[Provide the gallery owner's critique here]\n</gallery_owner_perspective>\n\n<curator_perspective>\n[Provide the curator's critique here]\n</curator_perspective>\n\n<twelve_year_old_perspective>\n[Provide the 12-year-old's critique here]\n</twelve_year_old_perspective>\n\n<nineteen_year_old_perspective>\n[Provide the 19-year-old's critique here]\n</nineteen_year_old_perspective>\n\n<fifty_year_old_perspective>\n[Provide the 50-year-old's critique here]\n</fifty_year_old_perspective>\n</critique>\n\nEnsure that each perspective's critique is distinct and reflects the unique viewpoint of that particular role or age group. Be creative and insightful in your analysis, while remaining respectful and constructive in your critiques.",
            "TEMPERATURE": 0.8,
            "MAX_TOKENS": 1500
        }
    }
    with open(PROMPTS_FILE, 'w') as f:
        json.dump(sample_prompts, f, indent=4)

with open(PROMPTS_FILE, 'r') as f:
    PROMPTS = json.load(f)

class LLMAnalyzer:
    def __init__(self, api_base_url: str, api_key: str, model: str, title: str = "", debug: bool = False):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.model = model
        self.title = title
        self.debug = debug
        if self.debug:
            logging.debug(f"{EMOJI_INFO} LLMAnalyzer initialized with model {model} and title '{title}'")

    def process_image(self, image_path: str, prompts: List[str], output_file: Optional[str] = None):
        logging.info(f"{EMOJI_PROCESSING} Processing image: {image_path}")
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        results = []
        for prompt in prompts:
            prompt_details = PROMPTS.get(prompt, {})
            prompt_text = prompt_details.get('PROMPT_TEXT', prompt)
            temperature = float(prompt_details.get('TEMPERATURE', 0.7))
            max_tokens = int(prompt_details.get('MAX_TOKENS', 1000))

            payload = {
                "model": self.model,
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

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.api_base_url, headers=headers, json=payload)

            if response.status_code == 200:
                logging.info(f"{EMOJI_SUCCESS} Prompt '{prompt}' processed successfully.")
                result = response.json()
                results.append({
                    "prompt": prompt,
                    "result": result
                })
            else:
                logging.error(f"{EMOJI_ERROR} Failed to process prompt '{prompt}'. Status code: {response.status_code}")
                logging.error(f"{EMOJI_ERROR} Response: {response.text}")
                results.append({
                    "prompt": prompt,
                    "error": response.text
                })

        if output_file:
            with open(output_file, "w") as f:
                json.dump(results, f, indent=4)
            logging.info(f"{EMOJI_COMPLETE} Results saved to {output_file}")
        else:
            print(json.dumps(results, indent=4))

def list_models(models: List[Dict[str, Any]]):
    """
    Lists all available models with their information (excluding API keys).

    Args:
        models (List[Dict[str, Any]]): List of model dictionaries.
    """
    print(f"{EMOJI_INFO} Available Models:")
    for model in models:
        print(f"  {EMOJI_INFO} Model {model['number']}: {model['name']}")
        print(f"      API URL: {model['api_url']}")
        print(f"      Model: {model['model']}\n")

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

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Analyze an image using a selected LLM (Language Model) API and generate a JSON file with the results."
    )
    parser.add_argument(
        "image_path",
        type=str,
        nargs='?',
        help="Path to the image file to be processed."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Comma-separated prompts or prompt IDs (e.g., 'Describe the image, P1, P2'). Use 'list' to display all prompts."
    )
    parser.add_argument(
        "--model",
        type=str,
        help=f"Model number for analysis (1-{len(MODELS)}) or 'list' to display all models."
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Optional output file path for the JSON results."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging."
    )

    args = parser.parse_args()

    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handle --model list and --prompt list
    if args.model and args.model.lower() == 'list':
        list_models(MODELS)

    if args.prompt and args.prompt.lower() == 'list':
        list_prompts(PROMPTS)

    # If either --model or --prompt is 'list', and no other arguments, exit
    if (args.model and args.model.lower() == 'list') or (args.prompt and args.prompt.lower() == 'list'):
        exit(0)

    # Ensure required arguments are provided for analysis
    if not args.image_path or not args.prompt or not args.model:
        parser.error("the following arguments are required for analysis: image_path, --prompt, --model")

    # Validate model number
    try:
        model_number = int(args.model)
        selected_model = next((model for model in MODELS if model['number'] == model_number), None)
        if not selected_model:
            logging.error(f"{EMOJI_ERROR} Invalid model number: {model_number}. Use '--model list' to see available models.")
            exit(1)
    except ValueError:
        logging.error(f"{EMOJI_ERROR} Invalid model value: {args.model}. It should be an integer between 1 and {len(MODELS)} or 'list'.")
        exit(1)

    # Initialize LLMAnalyzer
    analyzer = LLMAnalyzer(
        api_base_url=selected_model['api_url'],
        api_key=selected_model['api_key'],
        model=selected_model['model'],
        title=selected_model['name'],
        debug=args.debug
    )

    # Process the image
    prompts = [p.strip() for p in args.prompt.split(',')]
    analyzer.process_image(args.image_path, prompts, args.output)

if __name__ == "__main__":
    main()