import requests
import base64
import os
import json
import argparse
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import datetime
import hashlib
import sys

# Import database
from src.database.db_manager import DatabaseManager

# Load environment variables from .env file
load_dotenv()

# Import utilities
from src.utils.logger import get_global_logger
from src.utils.error_handler import ErrorCategory, error_context, handle_errors
from src.utils.debug_utils import debug_function, log_api_calls
from src.config.config_manager import get_config_value

# Get logger
logger = get_global_logger()

# Load status messages from .env or set default words
EMOJI_SUCCESS = get_config_value("EMOJI_SUCCESS", "SUCCESS")
EMOJI_WARNING = get_config_value("EMOJI_WARNING", "WARNING")
EMOJI_ERROR = get_config_value("EMOJI_ERROR", "ERROR")
EMOJI_INFO = get_config_value("EMOJI_INFO", "INFO")
EMOJI_PROCESSING = get_config_value("EMOJI_PROCESSING", "PROCESSING")

# Initialize database manager
db_manager = DatabaseManager()

# Global session cache for authenticated requests
_session_cache: Optional[requests.Session] = None
_session_url: Optional[str] = None


def get_authenticated_session(api_base_url: str, password: Optional[str] = None) -> requests.Session:
    """
    Get an authenticated session for the CLIP API.
    
    For Stable Diffusion Forge APIs that require Pinokio authentication,
    this function logs in and returns a session with auth cookies.
    
    Args:
        api_base_url: Base URL of the CLIP API
        password: Optional password for authentication. If not provided,
                 will try to get from CLIP_API_PASSWORD env variable
    
    Returns:
        requests.Session: Authenticated session (or regular session if no auth needed)
    """
    global _session_cache, _session_url
    
    # Return cached session if we have one for this URL
    if _session_cache and _session_url == api_base_url:
        # Test if session is still valid
        try:
            test_response = _session_cache.get(f"{api_base_url}/info", timeout=5)
            if test_response.status_code == 200:
                logger.debug("Using cached authenticated session")
                return _session_cache
            else:
                logger.debug("Cached session expired, re-authenticating")
        except:
            logger.debug("Cached session failed, re-authenticating")
    
    # Create new session
    session = requests.Session()
    
    # Get password from config if not provided
    if password is None:
        password = get_config_value("CLIP_API_PASSWORD")
    
    # If password provided, attempt authentication
    if password:
        try:
            logger.info("Authenticating with CLIP API...")
            login_url = f"{api_base_url}/pinokio/login"
            response = session.post(
                login_url,
                data={"password": password},
                allow_redirects=True,
                timeout=10
            )
            
            # Check if we got a session cookie
            if 'connect.sid' in session.cookies:
                logger.info("✅ Successfully authenticated with CLIP API")
                _session_cache = session
                _session_url = api_base_url
                return session
            else:
                logger.warning("No session cookie received, continuing without authentication")
        except Exception as e:
            logger.warning(f"Authentication failed: {e}. Continuing without authentication.")
    else:
        logger.debug("No password provided, using unauthenticated session")
    
    # Return regular session (no auth)
    return session


def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 string with error handling"""
    try:
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            logger.debug(f"Read {len(image_data)} bytes from {image_path}")
            encoded_string = base64.b64encode(image_data).decode("utf-8")
            logger.debug(f"Encoded image (first 100 chars): {encoded_string[:100]}")
            return encoded_string
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        raise Exception(f"Failed to encode image {image_path}: {e}")

def prompt_image(image_path: str, api_base_url: str, model: str, modes: List[str], 
                timeout: int = 60, password: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate prompts for an image using CLIP interrogator.
    
    Args:
        image_path: Path to the image file
        api_base_url: Base URL of the CLIP API
        model: CLIP model name to use
        modes: List of analysis modes (best, fast, classic, negative, caption)
        timeout: Request timeout in seconds
        password: Optional password for authentication
    
    Returns:
        Dict with status and prompt results
    """
    try:
        image_base64 = encode_image_to_base64(image_path)
        if not image_base64:
            return {"status": "error", "message": "Failed to encode image"}
        
        # Get authenticated session
        session = get_authenticated_session(api_base_url, password)
        
        prompts = {}
        headers = {"Content-Type": "application/json"}
        
        for mode in modes:
            payload = {
                "image": image_base64,
                "model": model,
                "mode": mode
            }
            
            logger.debug(f"Sending request to {api_base_url}/interrogator/prompt with mode: {mode}")
            
            try:
                response = session.post(
                    f"{api_base_url}/interrogator/prompt",
                    headers=headers,
                    json=payload,
                    timeout=300
                )
                response.raise_for_status()
                response_data = response.json()
                prompts[mode] = response_data
                logger.debug(f"Successfully processed mode: {mode}")
                
            except requests.exceptions.Timeout:
                logger.error(f"Timeout during prompt generation for mode: {mode}")
                prompts[mode] = {"status": "error", "message": "Request timeout"}
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for mode {mode}: {e}")
                prompts[mode] = {"status": "error", "message": str(e)}
            except Exception as e:
                logger.error(f"Unexpected error for mode {mode}: {e}")
                prompts[mode] = {"status": "error", "message": str(e)}
        
        return {"status": "success", "prompt": prompts}
        
    except Exception as e:
        logger.error(f"Failed to generate prompts: {e}")
        return {"status": "error", "message": str(e)}

def analyze_image_with_clip(image_path: str, api_base_url: str, model: str, modes: List[str], 
                           force_reprocess: bool = False, progress_callback=None, 
                           password: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze an image using CLIP interrogator with comprehensive error handling and progress updates.
    
    Args:
        image_path: Path to the image file
        api_base_url: Base URL of the CLIP API
        model: CLIP model name to use
        modes: List of analysis modes (best, fast, classic, negative, caption)
        force_reprocess: Force reprocessing even if cached
        progress_callback: Optional callback function for progress updates
        password: Optional password for authentication
    
    Returns:
        Dict with status and analysis results
    """
    try:
        logger.info(f"Starting CLIP analysis for {image_path}")
        
        # Validate inputs
        if not os.path.exists(image_path):
            return {"status": "error", "message": f"Image file not found: {image_path}"}
        
        if not api_base_url:
            return {"status": "error", "message": "API base URL not provided"}
        
        if not modes:
            return {"status": "error", "message": "No analysis modes specified"}
        
        # Get authenticated session
        session = get_authenticated_session(api_base_url, password)
        
        # Read and encode image
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            return {"status": "error", "message": f"Failed to read image file: {e}"}
        
        # Process each mode with progress updates
        results = {}
        for i, mode in enumerate(modes, 1):
            if progress_callback:
                progress_callback(step="CLIP", mode=mode)
            
            logger.debug(f"Processing CLIP mode {i}/{len(modes)}: {mode}")
            
            # Prepare payload for analysis
            payload = {
                "image": encoded_image,
                "model": model,
                "mode": mode
            }

            logger.debug(f"Sending analysis request to {api_base_url}/interrogator/analyze for mode: {mode}")

            headers = {
                "Content-Type": "application/json"
            }

            # Make the API request with authenticated session
            try:
                response = session.post(
                    f"{api_base_url}/interrogator/analyze", 
                    headers=headers, 
                    json=payload,
                    timeout=300
                )
                response.raise_for_status()
                result = response.json()
                
                # Ensure 'status' key is present
                if "status" not in result:
                    result["status"] = "success"
                
                results[mode] = result
                logger.debug(f"Successfully processed mode: {mode}")

            except requests.exceptions.Timeout:
                error_msg = f"CLIP API request timed out for mode: {mode}"
                logger.error(error_msg)
                results[mode] = {"status": "error", "message": error_msg}
                
            except requests.exceptions.ConnectionError:
                error_msg = f"Cannot connect to CLIP API at {api_base_url} for mode: {mode}"
                logger.error(error_msg)
                results[mode] = {"status": "error", "message": error_msg}
                
            except requests.exceptions.HTTPError as http_err:
                error_msg = f"HTTP error during CLIP analysis for mode {mode}: {http_err}"
                logger.error(error_msg)
                results[mode] = {"status": "error", "message": error_msg}
                
            except Exception as err:
                error_msg = f"Unexpected error during CLIP analysis for mode {mode}: {err}"
                logger.error(error_msg)
                results[mode] = {"status": "error", "message": error_msg}
        
        # Create final result structure
        final_result = {
            "status": "success",
            "model": model,
            "modes": modes,
            "results": results
        }
        
        logger.info(f"CLIP analysis completed successfully for {image_path}")
        return final_result

    except Exception as e:
        error_msg = f"Failed to analyze image {image_path}: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

def process_image_with_clip(image_path: str, api_base_url: str, model: str, modes: List[str], 
                           force_reprocess: bool = False, password: Optional[str] = None) -> Dict[str, Any]:
    """
    Process an image with CLIP analysis and return unified result structure with database integration.
    
    Args:
        image_path: Path to the image file
        api_base_url: Base URL of the CLIP API
        model: CLIP model name to use
        modes: List of analysis modes (best, fast, classic, negative, caption)
        force_reprocess: Force reprocessing even if cached in database
        password: Optional password for authentication. If not provided, 
                 will try to get from CLIP_API_PASSWORD env variable
    
    Returns:
        Dict with status and complete analysis results
    """
    try:
        logger.info(f"Processing image with CLIP: {image_path}")
        
        # Compute MD5 for database lookup
        image_md5 = compute_md5(image_path)
        
        # Check database for existing results (unless force reprocess is enabled)
        if not force_reprocess:
            existing_result = db_manager.get_result_by_md5(image_md5)
            if existing_result:
                logger.info(f"Found existing CLIP analysis in database for {image_path}")
                return {
                    "status": "success",
                    "message": "Retrieved from database",
                    "data": existing_result,
                    "from_database": True
                }
        
        # Generate prompts (with authentication)
        prompt_results = prompt_image(image_path, api_base_url, model, modes, password=password)
        if prompt_results.get("status") == "error":
            return {"status": "error", "message": f"Prompt generation failed: {prompt_results.get('message')}"}

        # Perform image analysis (with authentication)
        analysis_results = analyze_image_with_clip(image_path, api_base_url, model, modes, password=password)
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
            logger.info(f"Saved CLIP analysis to database for {image_path}")
        except Exception as db_error:
            logger.warning(f"Failed to save to database: {db_error}")

        logger.info(f"CLIP processing completed successfully for {image_path}")
        return output_data

    except Exception as e:
        error_msg = f"CLIP processing failed for {image_path}: {e}"
        logger.error(error_msg)
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
        logger.error(f"Failed to compute MD5 for {file_path}: {e}")
        return "unknown"

def save_json(data: Dict[str, Any], filename: str):
    """Save data to JSON file with error handling"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"{EMOJI_SUCCESS} Saved output to {filename}")
    except Exception as e:
        logger.error(f"{EMOJI_ERROR} Failed to save to {filename}: {e}")
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
    parser = argparse.ArgumentParser(
        description="Process an image using the CLIP API (Supports authenticated Forge/Pinokio APIs)."
    )
    parser.add_argument("image_path", type=str, help="Path to the image file.")
    parser.add_argument("--api_base_url", type=str, 
                       default=get_config_value("CLIP_API_URL", "http://localhost:7860"), 
                       help="Base URL of the CLIP API (default from CLIP_API_URL env or http://localhost:7860).")
    parser.add_argument("--model", type=str, 
                       default=get_config_value("CLIP_MODEL_NAME", "ViT-L-14/openai"), 
                       help="Model name to use for analysis (default from CLIP_MODEL_NAME env or ViT-L-14/openai).")
    parser.add_argument("--modes", type=str, nargs='+', 
                       default=get_config_value("CLIP_MODES", ["best", "fast"]), 
                       help="Modes for prompt generation (default from CLIP_MODES env or 'best,fast').")
    parser.add_argument("--password", type=str, 
                       default=get_config_value("CLIP_API_PASSWORD"),
                       help="Password for API authentication (default from CLIP_API_PASSWORD env).")
    parser.add_argument("--output", type=str, default="clip_output.json", 
                       help="Output JSON file.")
    parser.add_argument("--validate", action="store_true", 
                       help="Validate configuration before processing.")
    parser.add_argument("--force", action="store_true",
                       help="Force reprocessing even if result is cached.")
    
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
            if args.password:
                print("✅ Password provided for authentication")
            return 0

    # Process the image
    try:
        result = process_image_with_clip(
            args.image_path, 
            args.api_base_url, 
            args.model, 
            args.modes,
            force_reprocess=args.force,
            password=args.password
        )
        
        if result.get("status") == "success":
            save_json(result, args.output)
            print(f"✅ CLIP analysis completed successfully")
            if result.get("from_database"):
                print(f"   (Retrieved from cache)")
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
