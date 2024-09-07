import os
import json
import requests
import logging

def send_clip_request(data, api_url, timeout, config):
    """Send a request to the CLIP API."""
    try:
        response = requests.post(f"{api_url}/interrogator/prompt", json=data, timeout=timeout)
        response.raise_for_status()
        log_api_communication(api_url, "/interrogator/prompt", data, response, config)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"CLIP API request failed: {e}")
        logging.error(f"Request payload (without image): {json.dumps({k: v for k, v in data.items() if k != 'image'}, indent=2)}")
        return None

def send_llm_request(data, api_key):
    """Send a request to the LLM API."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"LLM API request failed: {e}")
        # Log request payload excluding 'image' data
        reduced_data = {k: v for k, v in data.items() if k != 'messages'}
        logging.error(f"Request payload: {json.dumps(reduced_data, indent=2)}")
        return None

def is_llm_json_valid(json_path):
    """Check if the LLM JSON file is valid (exists and is not null)."""
    if not os.path.exists(json_path):
        return False
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                return True
    except (IOError, json.JSONDecodeError):
        return False
    return False

def test_api(api_base_url: str, timeout: int) -> bool:
    """Test the API by hitting the health endpoint."""
    try:
        response = requests.get(f"{api_base_url}/info", timeout=timeout)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"API test failed: {e}")
        return False

def create_data(image_data, prompt_text, temperature, max_tokens, role, system_content, model, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    """Create the payload data for the API request."""
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": role, "content": prompt_text},
            {"role": role, "content": {"type": "image_url", "image_url": {"url": image_data}}}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty
    }

def log_api_communication(api_url, endpoint, request_data, response, config):
    """Log API communication if enabled in the configuration."""
    if config.log_api_communication:
        log_data = {
            "url": f"{api_url}{endpoint}",
            "request": {k: v for k, v in request_data.items() if k != 'image'},  # Exclude image data from log
            "response_status_code": response.status_code,
            "response_text": response.text
        }
        log_file_path = os.path.join(config.output_directory, 'api_communication_log.json')
        try:
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                json.dump(log_data, log_file, indent=2)
                log_file.write('\n')
        except IOError as e:
            logging.error(f"Failed to write API communication log: {e}")