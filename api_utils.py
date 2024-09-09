import logging
import time
import json
import os
from functools import wraps
from typing import Callable, Dict, Any, Optional
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