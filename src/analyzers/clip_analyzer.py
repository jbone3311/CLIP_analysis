import requests
import base64
import os
import json
import argparse
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import datetime
import hashlib
import sys

# Add src to path for database imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.db_manager import DatabaseManager

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

# Initialize database manager
db_manager = DatabaseManager()

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 string with error handling"""
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            logging.debug(f"Read {len(image_data)} bytes from {image_path}")
            encoded_string = base64.b64encode(image_data).decode("utf-8")
            logging.debug(f"Encoded image (first 100 chars): {encoded_string[:100]}")
            return encoded_string
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        raise Exception(f"Failed to encode image {image_path}: {e}")

def prompt_image(image_path: str, api_base_url: str, model: str, modes: List[str], timeout: int = 60) -> Dict[str, Any]:
    """Generate prompts for an image using CLIP interrogator"""
    try:
        image_base64 = encode_image_to_base64(image_path)
        if not image_base64:
            return {"status": "error", "message": "Failed to encode image"}
        
        prompts = {}
        headers = {"Content-Type": "application/json"}
        
        for mode in modes:
            payload = {
                "image": image_base64,
                "model": model,
                "mode": mode
            }
            
            logging.debug(f"Sending request to {api_base_url}/interrogator/prompt with mode: {mode}")
            
            try:
                response = requests.post(
                    f"{api_base_url}/interrogator/prompt",
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                response.raise_for_status()
                response_data = response.json()
                prompts[mode] = response_data
                logging.debug(f"Successfully processed mode: {mode}")
                
            except requests.exceptions.Timeout:
                logging.error(f"Timeout during prompt generation for mode: {mode}")
                prompts[mode] = {"status": "error", "message": "Request timeout"}
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed for mode {mode}: {e}")
                prompts[mode] = {"status": "error", "message": str(e)}
            except Exception as e:
                logging.error(f"Unexpected error for mode {mode}: {e}")
                prompts[mode] = {"status": "error", "message": str(e)}
        
        return {"status": "success", "prompt": prompts}
        
    except Exception as e:
        logging.error(f"Failed to generate prompts: {e}")
        return {"status": "error", "message": str(e)}

def analyze_image_with_clip(image_path: str, api_base_url: str, model: str, modes: List[str]) -> Dict[str, Any]:
    """Analyze an image using CLIP interrogator with comprehensive error handling"""
    try:
        logging.info(f"Starting CLIP analysis for {image_path}")
        
        # Validate inputs
        if not os.path.exists(image_path):
            return {"status": "error", "message": f"Image file not found: {image_path}"}
        
        if not api_base_url:
            return {"status": "error", "message": "API base URL not provided"}
        
        if not modes:
            return {"status": "error", "message": "No analysis modes specified"}
        
        # Read and encode image
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            return {"status": "error", "message": f"Failed to read image file: {e}"}
        
        # Prepare payload for analysis
        payload = {
            "image": encoded_image,
            "model": model,
            "modes": modes
        }

        logging.debug(f"Sending analysis request to {api_base_url}/interrogator/analyze")

        headers = {
            "Content-Type": "application/json"
        }

        # Make the API request
        try:
            response = requests.post(
                f"{api_base_url}/interrogator/analyze", 
                headers=headers, 
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            
            # Ensure 'status' key is present
            if "status" not in result:
                result["status"] = "success"
            
            logging.info(f"CLIP analysis completed successfully for {image_path}")
            return result

        except requests.exceptions.Timeout:
            error_msg = "CLIP API request timed out"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Cannot connect to CLIP API at {api_base_url}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        except requests.exceptions.HTTPError as http_err:
            error_msg = f"HTTP error during CLIP analysis: {http_err}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}
            
        except Exception as err:
            error_msg = f"Unexpected error during CLIP analysis: {err}"
            logging.error(error_msg)
            return {"status": "error", "message": error_msg}

    except Exception as e:
        error_msg = f"Failed to analyze image {image_path}: {e}"
        logging.error(error_msg)
        return {"status": "error", "message": error_msg}

def process_image_with_clip(image_path: str, api_base_url: str, model: str, modes: List[str], force_reprocess: bool = False) -> Dict[str, Any]:
    """Process an image with CLIP analysis and return unified result structure with database integration"""
    try:
        logging.info(f"Processing image with CLIP: {image_path}")
        
        # Compute MD5 for database lookup
        image_md5 = compute_md5(image_path)
        
        # Check database for existing results (unless force reprocess is enabled)
        if not force_reprocess:
            existing_result = db_manager.get_result_by_md5(image_md5)
            if existing_result:
                logging.info(f"Found existing CLIP analysis in database for {image_path}")
                return {
                    "status": "success",
                    "message": "Retrieved from database",
                    "data": existing_result,
                    "from_database": True
                }
        
        # Generate prompts
        prompt_results = prompt_image(image_path, api_base_url, model, modes)
        if prompt_results.get("status") == "error":
            return {"status": "error", "message": f"Prompt generation failed: {prompt_results.get('message')}"}

        # Perform image analysis
        analysis_results = analyze_image_with_clip(image_path, api_base_url, model, modes)
        if analysis_results.get("status") == "error":
            return {"status": "error", "message": f"Analysis failed: {analysis_results.get('message')}"}

        # Standardize directory format
        directory = os.path.dirname(image_path).replace("\\", "/")

        # Create unified result structure
        output_data = {
            "filename": os.path.basename(image_path),
            "directory": directory,
            "date_added": datetime.datetime.now().isoformat(),
            "md5": image_md5,
            "model": model,
            "modes": modes,
            "prompt": prompt_results.get("prompt", {}),
            "analysis_results": analysis_results,
            "status": "success"
        }

        # Save to database
        try:
            db_manager.insert_result(
                filename=output_data["filename"],
                directory=output_data["directory"],
                md5=image_md5,
                model=model,
                modes=json.dumps(modes),
                prompts=json.dumps(prompt_results.get("prompt", {})),
                analysis_results=json.dumps(analysis_results),
                settings=json.dumps({
                    "api_base_url": api_base_url,
                    "model": model,
                    "modes": modes
                })
            )
            logging.info(f"Saved CLIP analysis to database for {image_path}")
        except Exception as db_error:
            logging.warning(f"Failed to save to database: {db_error}")

        logging.info(f"CLIP processing completed successfully for {image_path}")
        return output_data

    except Exception as e:
        error_msg = f"CLIP processing failed for {image_path}: {e}"
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

def save_json(data: Dict[str, Any], filename: str):
    """Save data to JSON file with error handling"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logging.info(f"{EMOJI_SUCCESS} Saved output to {filename}")
    except Exception as e:
        logging.error(f"{EMOJI_ERROR} Failed to save to {filename}: {e}")
        raise

def validate_clip_config(api_base_url: str, model: str, modes: List[str]) -> List[str]:
    """Validate CLIP configuration and return list of errors"""
    errors = []
    
    if not api_base_url:
        errors.append("API base URL is required")
    
    if not model:
        errors.append("Model name is required")
    
    if not modes:
        errors.append("At least one analysis mode is required")
    
    valid_modes = ['best', 'fast', 'classic', 'negative', 'caption']
    invalid_modes = [mode for mode in modes if mode not in valid_modes]
    if invalid_modes:
        errors.append(f"Invalid modes: {invalid_modes}. Valid modes are: {valid_modes}")
    
    return errors

def main():
    """Main entry point for standalone CLIP analysis"""
    parser = argparse.ArgumentParser(description="Process an image using the CLIP API.")
    parser.add_argument("image_path", type=str, help="Path to the image file.")
    parser.add_argument("--api_base_url", type=str, default="http://localhost:7860", 
                       help="Base URL of the CLIP API.")
    parser.add_argument("--model", type=str, default="ViT-L-14", 
                       help="Model name to use for analysis.")
    parser.add_argument("--modes", type=str, nargs='+', default=["best", "fast"], 
                       help="Modes for prompt generation.")
    parser.add_argument("--output", type=str, default="clip_output.json", 
                       help="Output JSON file.")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate configuration before processing.")
    
    args = parser.parse_args()

    # Validate configuration if requested
    if args.validate:
        errors = validate_clip_config(args.api_base_url, args.model, args.modes)
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
        result = process_image_with_clip(args.image_path, args.api_base_url, args.model, args.modes)
        
        if result.get("status") == "success":
            save_json(result, args.output)
            print(f"✅ CLIP analysis completed successfully")
            return 0
        else:
            print(f"❌ CLIP analysis failed: {result.get('message')}")
            return 1
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
else:
    # This ensures process_image_with_clip is available when the module is imported
    __all__ = ['process_image_with_clip', 'analyze_image_with_clip', 'prompt_image']
