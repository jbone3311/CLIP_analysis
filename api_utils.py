import os
import requests
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from functools import wraps
from utils import safe_api_call

load_dotenv()

# Function to test the API
def test_api(api_base_url: str, timeout: int) -> bool:
    """
    Test the API by hitting the health endpoint.
    
    :param api_base_url: Base URL of the API.
    :param timeout: Timeout duration for the request.
    :return: True if the API is responsive, False otherwise.
    """
    try:
        response = requests.get(f"{api_base_url}/health", timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to send a request to the LLM API
@safe_api_call
def send_llm_request(data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Send a request to the LLM API.

    :param data: The payload to send to the API.
    :param api_key: The API key for authentication.
    :return: The response from the API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    api_url = os.getenv('LLM_API_URL', 'http://default-llm-url.com')
    try:
        response = requests.post(data['api_url'], json=data['payload'], headers=headers, timeout=data['timeout'])
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error in LLM API request: {str(e)}")
        return None

# Function to check if the LLM JSON data is valid
def is_llm_json_valid(json_data: dict) -> bool:
    """
    Check if the LLM JSON data is valid.

    :param json_data: The JSON data to check.
    :return: True if the data is valid, False otherwise.
    """
    required_keys = ['model', 'messages', 'temperature', 'max_tokens']
    return all(key in json_data for key in required_keys)

# Function to create the data payload for the LLM request
def create_data(image_url: str, prompt_text: str, temperature: float, max_tokens: int, role: str, system_content: str, model: str, top_p: float = 1.0, frequency_penalty: float = 0.0, presence_penalty: float = 0.0) -> dict:
    """
    Create the data payload for the LLM request.

    :param image_url: The URL of the image.
    :param prompt_text: The prompt text to send to the LLM.
    :param temperature: The temperature setting for the LLM.
    :param max_tokens: The maximum number of tokens for the LLM response.
    :param role: The role of the message sender.
    :param system_content: The system content for the LLM.
    :param model: The model to use for the LLM.
    :param top_p: The top-p setting for the LLM.
    :param frequency_penalty: The frequency penalty setting for the LLM.
    :param presence_penalty: The presence penalty setting for the LLM.
    :return: The data payload as a dictionary.
    """
    return {
        "model": model,
        "messages": [
            {
                "role": role,
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
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }

# Function to analyze an image in detail by sending it to the API with multiple caption types
@safe_api_call
def analyze_image_detailed(image_base64: str, model: str, caption_types: list, api_url: str, timeout: int, config) -> Dict[str, Any]:
    """
    Send a request to analyze an image using the CLIP model.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
    }
    payload = {
        "model": model,
        "image": image_base64,
        "detailed": True,
        "caption_types": caption_types
    }
    response = requests.post(f"{api_url}/interrogator/prompt", json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()

# Other functions in api_utils.py remain unchanged