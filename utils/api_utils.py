import json
import requests
import logging

# Function to test the API
def test_api(api_base_url: str, timeout: int) -> bool:
    """
    Test the API by hitting the health endpoint.
    
    :param api_base_url: Base URL of the API.
    :param timeout: Timeout duration for the request.
    :return: True if the API is responsive, False otherwise.
    """
    try:
        response = requests.get(f"{api_base_url}/info", timeout=timeout)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False

# Function to send a request to the LLM API
def send_llm_request(data: dict, api_key: str) -> dict:
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
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f'Error connecting to the API: {conn_err}')
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f'Timeout error: {timeout_err}')
    except requests.exceptions.RequestException as req_err:
        logging.error(f'An error occurred with the API request: {req_err}')
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
def analyze_image_detailed(image_base64: str, model: str, caption_types: list, api_base_url: str, timeout: int, config) -> dict:
    """
    Analyze an image in detail by sending it to the API with multiple caption types.

    :param image_base64: Base64 encoded image.
    :param model: Model name to use for analysis.
    :param caption_types: List of caption types to generate.
    :param api_base_url: Base URL of the API.
    :param timeout: Timeout duration for the request.
    :param config: Configuration object.
    :return: Detailed results including prompts and analysis data.
    """
    detailed_results = {"prompts": {}}
    for caption_type in caption_types:
        try:
            payload = {"image": image_base64, "clip_model_name": model, "mode": caption_type}
            
            if config.log_api_communication:
                logging.debug(f"API URL: {api_base_url}/interrogator/prompt")
                logging.debug(f"Payload (excluding image): {json.dumps({k: v for k, v in payload.items() if k != 'image'})}")

            response = requests.post(f"{api_base_url}/interrogator/prompt", json=payload, timeout=timeout)
            response.raise_for_status()

            if config.log_api_communication:
                logging.debug(f"Response: {response.status_code} - {response.text}")

            detailed_results["prompts"][caption_type] = response.json().get('prompt')
        except requests.exceptions.HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            detailed_results["prompts"][caption_type] = None
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f'Error connecting to the API: {conn_err}')
            detailed_results["prompts"][caption_type] = None
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f'Timeout error: {timeout_err}')
            detailed_results["prompts"][caption_type] = None
        except requests.exceptions.RequestException as req_err:
            logging.error(f'An error occurred with the API request: {req_err}')
            detailed_results["prompts"][caption_type] = None

    try:
        payload = {"image": image_base64, "clip_model_name": model}
        
        if config.log_api_communication:
            logging.debug(f"API URL: {api_base_url}/interrogator/analyze")
            logging.debug(f"Payload (excluding image): {json.dumps({k: v for k, v in payload.items() if k != 'image'})}")
    
        response = requests.post(f"{api_base_url}/interrogator/analyze", json=payload, timeout=timeout)
        response.raise_for_status()
    
        if config.log_api_communication:
            logging.debug(f"Response: {response.status_code} - {response.text}")
    
        analysis_data = response.json()
        detailed_results["analysis"] = analysis_data
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        detailed_results["analysis"] = None
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f'Error connecting to the API: {conn_err}')
        detailed_results["analysis"] = None
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f'Timeout error: {timeout_err}')
        detailed_results["analysis"] = None
    except requests.exceptions.RequestException as req_err:
        logging.error(f'An error occurred with the API request: {req_err}')
        detailed_results["analysis"] = None

    return detailed_results