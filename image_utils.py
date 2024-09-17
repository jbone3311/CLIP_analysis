import base64
import hashlib
import logging
from typing import Optional
import os

def generate_unique_code(image_path: str) -> str:
    """
    Generates a unique MD5 hash for the given image file.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The MD5 hash of the image file.
    """
    try:
        with open(image_path, "rb") as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        return file_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error generating unique code for {image_path}: {str(e)}")
        return f"error_{os.path.basename(image_path)}"

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """
    Encodes an image file to a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        Optional[str]: The base64 encoded string of the image content, or None if an error occurs.
    """
    try:
        # Check if the file exists and is accessible
        if not os.path.exists(image_path):
            logging.error(f"Image file does not exist: {image_path}")
            return None

        # Read the image file in binary mode
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            logging.info(f"Successfully encoded image to base64: {image_path}")
            return encoded_string
    except Exception as e:
        logging.error(f"Error encoding image to base64 {image_path}: {str(e)}")
        return None

# Keep other existing functions like resize_image