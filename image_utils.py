import base64
import hashlib
import logging
from typing import Optional
from PIL import Image, UnidentifiedImageError
from io import BytesIO, StringIO
import os
import io

def generate_unique_code(image_path: str) -> str:
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

def process_image_for_analysis(image_path: str) -> Optional[str]:
    try:
        if not os.path.exists(image_path):
            logging.error(f"Image file does not exist: {image_path}")
            return None

        with Image.open(image_path) as img:
            logging.info(f"Successfully opened image: {image_path}")
            logging.info(f"Image mode: {img.mode}, Size: {img.size}")
            if img.mode != 'RGB':
                img = img.convert('RGB')
                logging.info(f"Converted image to RGB mode")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
    except UnidentifiedImageError:
        logging.error(f"Cannot identify image file: {image_path}")
    except IOError as e:
        logging.error(f"IO Error opening image file: {image_path}. Error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error processing image {image_path}: {str(e)}")
    return None

def encode_image_to_base64(image_path: str) -> Optional[str]:
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding image to base64 {image_path}: {str(e)}")
        return None

# Keep other existing functions like resize_image