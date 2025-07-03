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
import datetime
import hashlib

# Determine the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Load environment variables from .env file in the script directory
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path)

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
PROMPT_CHOICES = os.getenv("PROMPT_CHOICES", "").split(',')

# Load prompts from LLM_Prompts.json in the script directory
PROMPTS_FILE = os.path.join(script_dir, 'LLM_Prompts.json')
if not os.path.exists(PROMPTS_FILE):
    # Create a sample LLM_Prompts.json file if it doesn't exist
    sample_prompts = {
        "P1": {
            "TITLE": "Detailed Image Description",
            "PROMPT_TEXT": "Describe the contents of the image accurately and thoroughly by following these steps:\n\n1. **Main Subject**: Identify the primary focus of the image. What immediately stands out?\n\n2. **Setting**: Describe whether the scene is indoors or outdoors and, if possible, estimate the time of day.\n\n3. **Details**: Expand on the key elements present in the image, covering:\n   - **People**: Mention their appearance, clothing, actions, and facial expressions.\n   - **Objects**: Identify significant objects, their positions, colors, and sizes.\n   - **Animals (if present)**: Describe the species, behavior, and appearance.\n   - **Natural Elements**: Note features like trees, plants, water, or landscapes.\n   - **Structures**: Describe buildings or other architectural elements, noting their style, size, and condition.\n\n4. **Colors and Lighting**: Describe the color palette and lighting in the image. Does it evoke a particular mood or atmosphere?\n\n5. **Text or Signage**: If there's any visible text or signage, include it in your description.\n\n6. **Noteworthy Features**: Highlight any unusual or striking features that stand out.\n\n7. **Composition**: Comment on the composition, including elements in the foreground, middle ground, and background.\n\n8. **Actions or Events**: If the image shows any ongoing actions or events, describe what seems to be happening.\n\n9. **Clarity**: If any part of the image is unclear, mention this.\n\nProvide this description in clear, concise language that could be helpful for someone who cannot see the image. Focus solely on observable details without assumptions or interpretations.",
            "TEMPERATURE": 0.7,
            "MAX_TOKENS": 3000
        },
        "P2": {
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
    Decorator to retry a function upon failure with exponential backoff.
    """
    def wrapper(*args, **kwargs):
        for attempt in range(Config.RETRY_LIMIT):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == Config.RETRY_LIMIT - 1:
                    logging.error(f"All {Config.RETRY_LIMIT} attempts failed.")
                    raise Exception(f"Failed after {Config.RETRY_LIMIT} attempts: {e}")
                logging.warning(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
    return wrapper

class LLMAnalyzer:
    def __init__(self, api_url: str, api_key: str, model_name: str, title: str, debug: bool = False):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.title = title
        self.debug = debug

    @retry_request
    def process_image(self, image_path: str, prompts: List[str]) -> List[Dict[str, Any]]:
        """Process an image with multiple prompts and return results"""
        logging.info(f"{EMOJI_PROCESSING} Processing image: {image_path}")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            raise Exception(f"Unable to read image file: {e}")

        results = []
        for prompt_id in prompts:
            try:
                result = self._process_single_prompt(prompt_id, image_data)
                results.append(result)
            except Exception as e:
                logging.error(f"Failed to process prompt '{prompt_id}': {e}")
                results.append({
                    "prompt": prompt_id,
                    "error": str(e),
                    "status": "failed"
                })
                
        return results

    def _process_single_prompt(self, prompt_id: str, image_data: str) -> Dict[str, Any]:
        """Process a single prompt with the image"""
        prompt_details = PROMPTS.get(prompt_id, {})
        prompt_text = prompt_details.get('PROMPT_TEXT', prompt_id)
        temperature = float(prompt_details.get('TEMPERATURE', 0.7))
        max_tokens = int(prompt_details.get('MAX_TOKENS', 1500))
        
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
        
        if self.debug:
            logging.debug(f"Sending request to {self.api_url}")
            logging.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(self.api_url, headers=headers, json=payload, timeout=Config.TIMEOUT)
        response.raise_for_status()
        
        response_data = response.json()
        
        if self.debug:
            logging.debug(f"Response: {json.dumps(response_data, indent=2)}")
        
        return {
            "prompt": prompt_id,
            "result": response_data,
            "status": "success"
        }

    def save_json(self, data: Dict[str, Any], output_file: str):
        """Save data to JSON file with error handling"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"{EMOJI_SUCCESS} Saved output to {output_file}")
        except Exception as e:
            logging.error(f"{EMOJI_ERROR} Failed to save to {output_file}: {e}")
            raise

def analyze_image_with_llm(image_path_or_directory: str, prompt_ids: List[str], model_number: int, output_file: str = None, debug: bool = False) -> Dict[str, Any]:
    """Main function to analyze an image with LLM"""
    try:
        # Configure logging levels
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        # Validate and retrieve model configuration
        model_config = next((model for model in MODELS if model['number'] == model_number), None)
        if not model_config:
            error_msg = f"Invalid model number: {model_number}. Available models: {[m['number'] for m in MODELS]}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}

        # Validate API key
        if not model_config.get('api_key'):
            error_msg = f"No API key provided for model {model_config['title']}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}

        # Initialize LLMAnalyzer
        analyzer = LLMAnalyzer(
            api_url=model_config['api_url'],
            api_key=model_config['api_key'],
            model_name=model_config['model_name'],
            title=model_config['title'],
            debug=debug
        )

        # Validate prompt IDs
        valid_prompts = [pid for pid in prompt_ids if pid in PROMPTS]
        if not valid_prompts:
            error_msg = f"No valid prompts found. Available prompts: {list(PROMPTS.keys())}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}

        # Process the image and get results
        api_responses = analyzer.process_image(image_path_or_directory, valid_prompts)

        # Check for any failed responses
        failed_responses = [resp for resp in api_responses if resp.get("status") == "failed"]
        if failed_responses and len(failed_responses) == len(api_responses):
            error_msg = f"All prompts failed for image {image_path_or_directory}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}

        # Create unified result structure
        output_data = {
            "filename": os.path.basename(image_path_or_directory),
            "directory": os.path.dirname(image_path_or_directory).replace("\\", "/"),
            "date_added": datetime.datetime.now().isoformat(),
            "md5": compute_md5(image_path_or_directory) if os.path.isfile(image_path_or_directory) else "N/A",
            "model": model_config['model_name'],
            "model_title": model_config['title'],
            "prompts": {pid: PROMPTS[pid] for pid in valid_prompts},
            "api_responses": api_responses,
            "status": "success"
        }

        # Save to file if output_file is specified
        if output_file:
            analyzer.save_json(output_data, output_file)

        logging.info(f"LLM analysis completed successfully for {image_path_or_directory}")
        return output_data

    except Exception as e:
        error_msg = f"LLM analysis failed for {image_path_or_directory}: {e}"
        logging.error(error_msg)
        return {"status": "error", "message": error_msg}

def compute_md5(file_path: str) -> str:
    """Compute MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logging.error(f"Failed to compute MD5 for {file_path}: {e}")
        return "unknown"

def validate_llm_config(model_number: int, prompt_ids: List[str]) -> List[str]:
    """Validate LLM configuration and return list of errors"""
    errors = []
    
    # Validate model
    model_config = next((model for model in MODELS if model['number'] == model_number), None)
    if not model_config:
        errors.append(f"Invalid model number: {model_number}")
    elif not model_config.get('api_key'):
        errors.append(f"No API key provided for model {model_config['title']}")
    
    # Validate prompts
    if not prompt_ids:
        errors.append("No prompts specified")
    else:
        invalid_prompts = [pid for pid in prompt_ids if pid not in PROMPTS]
        if invalid_prompts:
            errors.append(f"Invalid prompts: {invalid_prompts}")
    
    return errors

def main():
    """Main entry point for standalone LLM analysis"""
    parser = argparse.ArgumentParser(description="LLM Analysis")
    parser.add_argument("image_path_or_directory", type=str, help="Path to the image file or directory.")
    parser.add_argument("--prompt", type=str, help="Comma-separated prompt IDs.")
    parser.add_argument("--model", type=int, required=True, help="Model number for analysis.")
    parser.add_argument("--output", type=str, help="Output file path for the JSON results.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")
    parser.add_argument("--validate", action="store_true", help="Validate configuration before processing.")
    parser.add_argument("--list-models", action="store_true", help="List all available models.")
    parser.add_argument("--list-prompts", action="store_true", help="List all available prompts.")
    
    args = parser.parse_args()

    # Handle list commands
    if args.list_models:
        print("Available models:")
        for model in MODELS:
            print(f"  {model['number']}: {model['title']} ({model['model_name']})")
        return 0
    
    if args.list_prompts:
        print("Available prompts:")
        for prompt_id, prompt_data in PROMPTS.items():
            print(f"  {prompt_id}: {prompt_data.get('TITLE', 'No title')}")
        return 0

    # Use prompt choices from .env if not provided via command line
    prompt_ids = [p.strip() for p in (args.prompt or ','.join(PROMPT_CHOICES)).split(',') if p.strip()]

    # Validate configuration if requested
    if args.validate:
        errors = validate_llm_config(args.model, prompt_ids)
        if errors:
            print("❌ Configuration errors found:")
            for error in errors:
                print(f"   • {error}")
            return 1
        else:
            print("✅ Configuration is valid")
            return 0

    # Process the image
    try:
        result = analyze_image_with_llm(args.image_path_or_directory, prompt_ids, args.model, args.output, args.debug)
        
        if result.get("status") == "success":
            print(f"✅ LLM analysis completed successfully")
            return 0
        else:
            print(f"❌ LLM analysis failed: {result.get('message')}")
            return 1
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
