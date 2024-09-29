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

# Load prompts from LLM_Prompts.json
PROMPTS_FILE = 'LLM_Prompts.json'

if not os.path.exists(PROMPTS_FILE):
    # Create a sample LLM_Prompts.json file if it doesn't exist
    sample_prompts = {
        "PROMPT1": {
            "TITLE": "Detailed Image Description",
            "PROMPT_TEXT": "Describe the contents of the image accurately and thoroughly by following these steps:\n\n1. **Main Subject**: Identify the primary focus of the image. What immediately stands out?\n\n2. **Setting**: Describe whether the scene is indoors or outdoors and, if possible, estimate the time of day.\n\n3. **Details**: Expand on the key elements present in the image, covering:\n   - **People**: Mention their appearance, clothing, actions, and facial expressions.\n   - **Objects**: Identify significant objects, their positions, colors, and sizes.\n   - **Animals (if present)**: Describe the species, behavior, and appearance.\n   - **Natural Elements**: Note features like trees, plants, water, or landscapes.\n   - **Structures**: Describe buildings or other architectural elements, noting their style, size, and condition.\n\n4. **Colors and Lighting**: Describe the color palette and lighting in the image. Does it evoke a particular mood or atmosphere?\n\n5. **Text or Signage**: If there’s any visible text or signage, include it in your description.\n\n6. **Noteworthy Features**: Highlight any unusual or striking features that stand out.\n\n7. **Composition**: Comment on the composition, including elements in the foreground, middle ground, and background.\n\n8. **Actions or Events**: If the image shows any ongoing actions or events, describe what seems to be happening.\n\n9. **Clarity**: If any part of the image is unclear, mention this.\n\nProvide this description in clear, concise language that could be helpful for someone who cannot see the image. Focus solely on observable details without assumptions or interpretations.",
            "TEMPERATURE": 0.7,
            "MAX_TOKENS": 3000
        },
        "PROMPT2": {
            "TITLE": "Art Critique from Multiple Perspectives",
            "PROMPT_TEXT": "You are an art critic tasked with providing a comprehensive critique of an image from multiple perspectives. Your goal is to analyze the image visually, interpret its meaning, and describe how it appears and what it inspires from different viewpoints.\n\nExamine the image carefully and provide a critique from each of the following perspectives:\n\n1. Artist\n2. Gallery owner\n3. Curator\n4. 12-year-old\n5. 19-year-old\n6. 50-year-old\n\nFor each perspective, consider the following aspects:\n- Visual elements (composition, color, style, technique)\n- Emotional impact\n- Potential meaning or symbolism\n- How it relates to current trends or historical context (if applicable)\n- Personal interpretation based on the specific perspective\n\nStructure your response as follows:\n\n<critique>\n<artist_perspective>\n[Provide the artist's critique here]\n</artist_perspective>\n\n<gallery_owner_perspective>\n[Provide the gallery owner's critique here]\n</gallery_owner_perspective>\n\n<curator_perspective>\n[Provide the curator's critique here]\n</curator_perspective>\n\n<twelve_year_old_perspective>\n[Provide the 12-year-old's critique here]\n</twelve_year_old_perspective>\n\n<nineteen_year_old_perspective>\n[Provide the 19-year-old's critique here]\n</nineteen_year_old_perspective>\n\n<fifty_year_old_perspective>\n[Provide the 50-year-old's critique here]\n</fifty_year_old_perspective>\n</critique>\n\nEnsure that each perspective's critique is distinct and reflects the unique viewpoint of that particular role or age group. Be creative and insightful in your analysis, while remaining respectful and constructive in your critiques.",
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
                logging.info(f"Response from API: {response.json()}")  # Log the entire response
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
        
        output_data = {
            "image": absolute_image_path,
            "model": self.model_name,
            "prompts": {
                "results": results
            }
        }

        if output_file:
            try:
                self.save_json(output_data, output_file)
                logging.info(f"{EMOJI_SUCCESS} Results saved to {output_file}")
            except IOError as e:
                logging.error(f"{EMOJI_ERROR} Failed to save results: {e}")
        else:
            print(json.dumps(output_data, indent=4))

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

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Analyze an image or a directory of images using a selected LLM (Language Model) API and generate a JSON file with the results."
    )
    parser.add_argument(
        "image_path_or_directory",
        type=str,
        nargs='?',
        help="Path to the image file or directory to be processed."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Comma-separated prompts or prompt IDs (e.g., 'PROMPT1,PROMPT2'). Use 'list' to display all prompts."
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
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Print arguments for debugging
    print(f"Arguments: {args}")
    
    # Configure logging levels
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle --model list and --prompt list
    if args.model and args.model.lower() == 'list':
        list_models(MODELS)
        sys.exit(0)
    
    if args.prompt and args.prompt.lower() == 'list':
        list_prompts(PROMPTS)
        sys.exit(0)
    
    # If either --model or --prompt is 'list', and no other arguments, exit
    if (args.model and args.model.lower() == 'list') or (args.prompt and args.prompt.lower() == 'list'):
        sys.exit(0)
    
    # Ensure required arguments are provided for analysis
    if not args.image_path_or_directory or not args.prompt or not args.model:
        logging.error(f"{EMOJI_ERROR} Missing required arguments: image_path_or_directory, --prompt, --model")
        sys.exit(1)
    
    # Validate and retrieve model configuration
    try:
        model_number = int(args.model)
        # Check if model_number exists in MODELS
        model_config = next((model for model in MODELS if model['number'] == model_number), None)
        if not model_config:
            logging.error(f"{EMOJI_ERROR} Invalid model number: {args.model}. Use '--model list' to see available models.")
            sys.exit(1)
    except ValueError:
        logging.error(f"{EMOJI_ERROR} Invalid model value: {args.model}. It should be an integer between 1 and {len(MODELS)} or 'list'.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"{EMOJI_ERROR} {e}")
        sys.exit(1)
    
    # Initialize LLMAnalyzer
    analyzer = LLMAnalyzer(
        api_url=model_config['api_url'],
        api_key=model_config['api_key'],
        model_name=model_config['model_name'],
        title=model_config['title'],
        debug=args.debug
    )
    
    # Process the image
    prompts = [p.strip() for p in args.prompt.split(',') if p.strip()]
    if not prompts:
        logging.error(f"{EMOJI_ERROR} No valid prompts provided.")
        sys.exit(1)
    
    analyzer.process_image(args.image_path_or_directory, prompts, args.output)

if __name__ == "__main__":
    main()