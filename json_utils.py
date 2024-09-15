import os
import json
import logging
from typing import Dict, Any, List, Set

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

def get_existing_json_files(directory: str) -> Set[str]:
    json_files = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.json'):
                json_files.add(file)
    return json_files

def should_process_file(file_path: str, existing_files: List[str], analyzer_name: str, config) -> bool:
    json_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_{analyzer_name}.json"
    if json_filename in existing_files:
        json_path = os.path.join(config.output_directory, json_filename)
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                existing_data = json.load(f)
            
            # Check if all caption types are already processed
            existing_types = set(existing_data.get('analysis', {}).keys())
            required_types = set(config.caption_types)
            
            if required_types.issubset(existing_types):
                logging.info(f"Skipping {file_path}, all required caption types already processed.")
                return False
    return True

def process_json_to_txt(config, json_data: Dict[str, Any], output_dir: str):
    if not config.process_json_to_txt:
        return
        return
    filename = json_data['file_info']['filename']
    base_name = os.path.splitext(filename)[0]
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