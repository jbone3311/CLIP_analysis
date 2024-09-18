# utils.py

import os
import base64
import hashlib
import logging
import json

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def generate_unique_code(image_path: str) -> str:
    hasher = hashlib.md5()
    with open(image_path, "rb") as f:
        buf = f.read(8192)
        while buf:
            hasher.update(buf)
            buf = f.read(8192)
    return hasher.hexdigest()

def setup_logging(config):
    """
    Setup logging configurations based on the configuration values.
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.logging_level.upper(), logging.INFO))

    formatter = logging.Formatter(config.logging_format, datefmt='%Y-%m-%d %H:%M:%S')

    # File Handler
    file_handler = logging.FileHandler('processing.log')
    file_handler.setLevel(getattr(logging, config.logging_level.upper(), logging.INFO))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.logging_level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Suppress noisy loggers
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def save_json(data: dict, path: str):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)
