import base64
import hashlib
import requests
import os
import logging
from functools import wraps

def safe_api_call(func):
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

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        logging.error(f"Image file not found: {image_path}")
        return None
    except Exception as e:
        logging.exception(f"Error encoding image {image_path}: {str(e)}")
        return None

def generate_unique_code(file_path):
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
def analyze_image_detailed(image_base64, model, caption_types, api_url, timeout, config):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"
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

def get_existing_json_files(directory):
    existing_files = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                existing_files.add(file)
    return existing_files

def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('image_analysis.log')
        ]
    )

def validate_directory(directory):
    if not os.path.isdir(directory):
        raise ValueError(f"The specified path is not a valid directory: {directory}")
    if not os.access(directory, os.R_OK):
        raise PermissionError(f"You don't have read permissions for the directory: {directory}")

def validate_api_key():
    if 'OPENAI_API_KEY' not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set")
