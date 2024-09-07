import json
import os
import logging
from config import mask_api_key
from utils.image_utils import encode_image_to_base64, generate_unique_code
from utils.json_utils import save_json, get_existing_json_files
from utils.api_utils import send_llm_request, is_llm_json_valid, create_data
from constants import DEFAULTS

def process_llm_images(config, api_url, timeout):
    """
    Process images in a directory and send them for LLM analysis.

    Args:
        config: Configuration object.
        api_url: Base URL of the API.
        timeout: Timeout duration for the request.
    """
    failed_images = []
    images_to_process = []
    existing_json_files = []

    # Traverse the image directory and its subdirectories
    for subdir in os.listdir(config.image_directory):
        subdir_path = os.path.join(config.image_directory, subdir)
        if os.path.isdir(subdir_path):
            logging.debug(f"Looking into directory: {subdir_path}")
            batch_json_dir = os.path.join(subdir_path, 'json')
            os.makedirs(batch_json_dir, exist_ok=True)

            # Get existing JSON files
            existing_json_files += get_existing_json_files(batch_json_dir)

            for root, _, files in os.walk(subdir_path):
                logging.debug(f"Processing images in directory: {root}")
                image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg'))]
                for file in image_files:
                    images_to_process.append((root, file, batch_json_dir, subdir))

    total_images = len(images_to_process)
    if total_images == 0:
        logging.info("No images found to process.")
        return failed_images

    logging.info(f"Total images to process: {total_images}")

    # Initialize counters and timers
    image_counter = len(existing_json_files)
    total_processing_time = 0

    for root, file, batch_json_dir, subdir in images_to_process:
        llm_json_output_filename = f"{subdir}_{os.path.splitext(file)[0]}_llm_analysis.json"
        llm_json_full_path = os.path.join(batch_json_dir, llm_json_output_filename)

        # Process LLM analysis only if the JSON file does not exist
        if llm_json_output_filename not in existing_json_files:
            logging.info(f"LLM JSON file is invalid or does not exist for {file}. Running LLM analysis.")
            llm_results = {}

            # Hardcoded OpenAI settings
            openai_enabled = config.llms.get('LLM_1', {}).get('enabled', False)
            if openai_enabled:
                logging.info(f"Running LLM analysis using OpenAI for {file}.")
                for prompt_id in config.selected_prompts:
                    image_base64 = encode_image_to_base64(os.path.join(root, file))
                    data = {
                        "model": config.llm_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": DEFAULTS['Prompt Options'][prompt_id]['PROMPT_TEXT']},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "temperature": DEFAULTS['Prompt Options'][prompt_id]['TEMPERATURE'],
                        "max_tokens": DEFAULTS['Prompt Options'][prompt_id]['MAX_TOKENS'],
                        "top_p": 1.0,
                        "frequency_penalty": 0.0,
                        "presence_penalty": 0.0
                    }
                    logging.debug(f"Sending LLM request for prompt ID {prompt_id}")
                    logging.debug(f"Data payload: {json.dumps(data, indent=2)}")
                    api_key = config.get_openai_api_key()
                    logging.debug(f"Using API Key: {mask_api_key(api_key)}")
                    response = send_llm_request(data, api_key)
                    if response:
                        logging.debug(f"Received response for prompt ID {prompt_id}")
                        llm_results[prompt_id] = response['choices'][0]['message']['content']
                    else:
                        logging.warning(f"No response received for prompt ID {prompt_id}.")
                        llm_results[prompt_id] = None

            # Additional LLMs from config
            for llm_key, llm_config in config.llms.items():
                if llm_key != 'LLM_1' and llm_config['enabled']:
                    for prompt_id in config.selected_prompts:
                        image_base64 = encode_image_to_base64(os.path.join(root, file))
                        data = {
                            "model": config.llm_model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": DEFAULTS['Prompt Options'][prompt_id]['PROMPT_TEXT']},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{image_base64}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            "temperature": DEFAULTS['Prompt Options'][prompt_id]['TEMPERATURE'],
                            "max_tokens": DEFAULTS['Prompt Options'][prompt_id]['MAX_TOKENS'],
                            "top_p": 1.0,
                            "frequency_penalty": 0.0,
                            "presence_penalty": 0.0
                        }
                        logging.debug(f"Sending LLM request for prompt ID {prompt_id}")
                        logging.debug(f"Data payload: {json.dumps(data, indent=2)}")
                        logging.debug(f"Using API Key: {mask_api_key(llm_config['api_key'])}")
                        response = send_llm_request(data, llm_config['api_key'])
                        if response:
                            logging.debug(f"Received response for prompt ID {prompt_id}")
                            llm_results[prompt_id] = response['choices'][0]['message']['content']
                        else:
                            logging.warning(f"No response received for prompt ID {prompt_id}.")
                            llm_results[prompt_id] = None

            # Check if llm_results is not empty before saving
            if llm_results:
                try:
                    save_json(llm_json_full_path, llm_results)
                except Exception as e:
                    logging.error(f"Failed to save LLM JSON for {file}: {e}")
                    failed_images.append(file)
            else:
                logging.info(f"No LLM results for {file}. Skipping saving LLM JSON.")

    if failed_images:
        logging.error(f"Failed to process the following images: {failed_images}")

    logging.info("LLM analysis completed successfully.")
    return failed_images