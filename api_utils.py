import logging
import time
import json
import os
from functools import wraps
from typing import Callable, Dict, Any
import requests

def log_api_conversation(logger: logging.Logger, data: Dict[str, Any]):
    logger.debug("API Conversation:")
    logger.debug(json.dumps(data, indent=2))

def retry_with_backoff(max_retries: int = 3, backoff_factor: int = 2):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    wait = backoff_factor ** retries
                    logging.warning(f"Request failed: {e}. Retrying in {wait} seconds...")
                    time.sleep(wait)
                    retries += 1
            return func(*args, **kwargs)
        return wrapper
    return decorator

def create_llm_data(image_url: str, prompt_text: str, temperature: float, max_tokens: int, model: str) -> Dict[str, Any]:
    """
    Create the data payload for the LLM request.

    :param image_url: The URL of the image.
    :param prompt_text: The prompt text to send to the LLM.
    :param temperature: The temperature setting for the LLM.
    :param max_tokens: The maximum number of tokens for the LLM response.
    :param model: The model to use for the LLM.
    :return: The data payload as a dictionary.
    """
    if not isinstance(temperature, float) or not 0 <= temperature <= 1:
        raise ValueError("Temperature must be a float between 0 and 1")
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("max_tokens must be a positive integer")
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

@retry_with_backoff()
def send_llm_request(data: Dict[str, Any], api_key: str, api_url: str, timeout: float = 30.0) -> Dict[str, Any]:
    llm_logger = logging.getLogger('LLM_API')
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    try:
        response = requests.post(api_url, json=data, headers=headers, timeout=timeout)
        response.raise_for_status()
        response_data = response.json()
        log_api_conversation(llm_logger, {"request": data, "response": response_data})
        return response_data
    except requests.RequestException as e:
        llm_logger.error(f"Error in LLM API request: {str(e)}")
        llm_logger.error(f"Response content: {e.response.text if e.response else 'No response content'}")
        raise

def safe_api_call(func: Callable[..., Dict[str, Any]]) -> Callable[..., Optional[Dict[str, Any]]]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            logging.error(f"API call failed: {str(e)}")
            return None
    return wrapper

@safe_api_call
def analyze_image_detailed(image_base64: str, model: str, caption_types: list, api_url: str, timeout: float) -> Dict[str, Any]:
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
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error in analyze_image_detailed: {str(e)}")
        logging.error(f"Response content: {e.response.text if e.response else 'No response content'}")
        raise