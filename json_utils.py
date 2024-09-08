import os
import json
import logging
import time

def save_json(file_path, data):
    """
    Save data to a JSON file.

    Args:
        file_path: Path to the JSON file.
        data: Data to be saved.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        logging.info(f"JSON output created: {file_path}")
    except IOError as e:
        logging.error(f"Failed to create or write to file: {e}, Path attempted: {file_path}")

def get_existing_json_files(directory):
    """
    Get the list of existing JSON files in the given directory.

    Args:
        directory: Directory to search for JSON files.

    Returns:
        list: List of JSON filenames found.
    """
    json_files = []
    for root, _, files in os.walk(directory):
        json_files.extend([file for file in files if file.lower().endswith('_clip_analysis.json')])
    return json_files

def process_existing_json_files(config):
    """
    Process existing JSON files and generate text files containing prompt lists.

    Args:
        config: Configuration object.
    """
    clip_analysis_dir = os.path.join(config.output_directory, 'CLIP_analysis')
    os.makedirs(clip_analysis_dir, exist_ok=True)

    for subdir in os.listdir(config.image_directory):
        subdir_path = os.path.join(config.image_directory, subdir)
        if os.path.isdir(subdir_path):
            logging.debug(f"Looking into JSON directory: {subdir_path}")
            batch_json_dir = os.path.join(subdir_path, 'json')
            if not os.path.exists(batch_json_dir):
                logging.info(f"JSON directory does not exist: {batch_json_dir}")
                continue
            else:
                logging.info(f"Found JSON directory: {batch_json_dir}")

            for root, _, files in os.walk(batch_json_dir):
                logging.debug(f"Processing existing JSON files in directory: {root}")
                prompt_lists = {caption_type: [] for caption_type in config.caption_types}

                json_files = [file for file in files if file.lower().endswith('_clip_analysis.json')]
                if not json_files:
                    logging.info(f"No JSON files found in {root}")
                    continue

                for json_file in json_files:
                    json_full_path = os.path.join(root, json_file)
                    logging.debug(f"Reading JSON file: {json_full_path}")
                    try:
                        with open(json_full_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                    except Exception as e:
                        logging.error(f"Failed to read JSON file {json_full_path}: {e}")
                        continue

                    for caption_type in config.caption_types:
                        if caption_type in data.get('prompts', {}):
                            prompt = data['prompts'][caption_type]
                            if prompt:
                                prompt_lists[caption_type].append(prompt)

                if config.create_prompt_list:
                    for caption_type, prompts in prompt_lists.items():
                        if prompts:
                            list_filename = f"{subdir}_{caption_type}_Prompts.txt"
                            list_path = os.path.join(clip_analysis_dir, list_filename)
                            logging.debug(f"Writing prompt list file: {list_path}")
                            try:
                                with open(list_path, config.list_file_mode, encoding='utf-8') as f:
                                    f.write('\n'.join(prompts))
                                logging.info(f"{time.strftime('%d/%m/%y %H:%M')} {list_filename}")
                            except Exception as e:
                                logging.error(f"Failed to write to file {list_path}: {e}")