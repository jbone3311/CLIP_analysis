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

def validate_directory(directory: str) -> None:
    """
    Validate if a directory exists and is accessible.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"The specified path is not a valid directory: {directory}")
    if not os.access(directory, os.R_OK):
        raise PermissionError(f"You don't have read permissions for the directory: {directory}")
