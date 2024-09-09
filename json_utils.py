import os
import json
import logging
from typing import Dict, Any, List

def save_json(file_path: str, data: Dict[str, Any]) -> None:
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
            
            # Update file_info
            existing_data['file_info'] = data['file_info']
            
            # Merge analysis results
            for mode, result in data['analysis'].items():
                if mode not in existing_data['analysis']:
                    existing_data['analysis'][mode] = result
                elif result['model'] != existing_data['analysis'][mode]['model']:
                    existing_data['analysis'][f"{mode}_{result['model']}"] = result
            
            data = existing_data
        
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        logging.info(f"JSON output created/updated: {file_path}")
    except IOError as e:
        logging.error(f"Failed to create or write to file: {e}, Path attempted: {file_path}")

def get_existing_json_files(directory: str) -> List[str]:
    json_files = []
    for root, _, files in os.walk(directory):
        json_files.extend([file for file in files if file.lower().endswith('.json')])
    return json_files

def should_process_file(image_path: str, json_path: str, analyzer_name: str, config) -> bool:
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                existing_data = json.load(f)
            
            # Check if all enabled modes are already processed
            existing_modes = set(existing_data['analysis'].keys())
            required_modes = set(config._get_enabled_modes())
            
            if required_modes.issubset(existing_modes):
                logging.info(f"Skipping {image_path}, all required modes already processed.")
                return False
        except json.JSONDecodeError:
            logging.warning(f"Invalid JSON file: {json_path}. Will reprocess.")
            return True
    else:
        logging.info(f"JSON file not found for {image_path}. Will process.")
    return True

def process_json_to_txt(config, json_data: Dict[str, Any], output_dir: str):
    if not config.process_json_to_txt:
        return

    filename = json_data['file_info']['filename']
    base_name = os.path.splitext(filename)[0]

    for mode, content in json_data['analysis'].items():
        if isinstance(content, str):
            txt_filename = f"{base_name}_{mode}.txt"
            txt_path = os.path.join(output_dir, txt_filename)
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"Created txt file: {txt_path}")

def process_existing_json_files(config):
    logging.info("Processing existing JSON files...")
    json_files = get_existing_json_files(config.image_directory)
    
    for json_file in json_files:
        file_path = os.path.join(config.image_directory, json_file)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Process the JSON data as needed, but don't create any txt files
            # You can add any necessary processing logic here
            
            logging.info(f"Processed {json_file}")
        except Exception as e:
            logging.error(f"Error processing {json_file}: {str(e)}")
    
    logging.info("Finished processing existing JSON files")