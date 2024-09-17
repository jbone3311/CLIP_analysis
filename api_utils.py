import logging
import time
import json
import os
from functools import wraps
from typing import Callable, Dict, Any, Optional
import requests

def log_api_conversation(logger: logging.Logger, data: Dict[str, Any], log_conversation: bool):
    if log_conversation:
        logger.debug("API Conversation:")
        logger.debug(json.dumps(data, indent=2))

def retry_with_backoff(max_retries: int = 5, initial_wait: float = 1, backoff_factor: float = 2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            wait_time = initial_wait
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    if isinstance(e, requests.HTTPError) and e.response.status_code == 500:
                        logging.warning(f"Server error (500). Retrying in {wait_time:.2f} seconds...")
                    else:
                        logging.warning(f"Request failed: {e}. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                    wait_time *= backoff_factor
            raise Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator

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
        log_api_conversation(llm_logger, {"request": data, "response": response_data}, True)
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