import base64
import hashlib
import requests
import os
import logging
from functools import wraps
from PIL import Image
import io
from typing import Optional, Dict, Any, Callable

def safe_api_call(func: Callable) -> Callable:
    """
    Decorator to safely handle API calls and log errors.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logging.exception(f"Unexpected error in API call: {str(e)}")
            return {"error": "An unexpected error occurred"}
    return wrapper

def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string.
    """
    with Image.open(image_path) as image:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def generate_unique_code(file_path: str) -> Optional[str]:
    """
    Generate a unique hash code for a file.
    """
    try:
        with open(file_path, "rb") as f:
            file_hash = hashlib.blake2b()
            for chunk in iter(lambda: f.read(8192), b""):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except Exception as e:
        logging.exception(f"Error generating unique code for {file_path}: {str(e)}")
        return None

@safe_api_call
def analyze_image_detailed(image_base64: str, model: str, caption_types: list, api_url: str, timeout: int, config: Any) -> Dict[str, Any]:
    """
    Send a request to analyze an image in detail.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.get_openai_api_key()}"
    }
    payload = {
        "model": model,
        "image": image_base64,
        "detailed": True,
        "caption_types": caption_types
    }
    response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()

def validate_directory(directory: str) -> None:
    """
    Validate if a directory exists and is accessible.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"The specified path is not a valid directory: {directory}")
    if not os.access(directory, os.R_OK):
        raise PermissionError(f"You don't have read permissions for the directory: {directory}")

def validate_api_key() -> None:
    """
    Validate if the OPENAI_API_KEY environment variable is set.
    """
    if 'OPENAI_API_KEY' not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set")
