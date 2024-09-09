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

def should_process_file(file_path: str, existing_files: List[str], analyzer_name: str, config) -> bool:
    json_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_{analyzer_name}.json"
    if json_filename in existing_files:
        with open(os.path.join(config.output_directory, json_filename), 'r') as f:
            existing_data = json.load(f)
        
        # Check if all enabled modes are already processed
        existing_modes = set(existing_data['analysis'].keys())
        required_modes = set(config._get_enabled_modes())
        
        if required_modes.issubset(existing_modes):
            logging.info(f"Skipping {file_path}, all required modes already processed.")
            return False
    return True

def process_existing_json_files(config):
    logging.info("Processing existing JSON files...")
    json_files = get_existing_json_files(config.output_directory)
    
    # Dictionary to store prompts for each mode
    mode_prompts = {mode: [] for mode in config._get_enabled_modes()}
    
    for json_file in json_files:
        file_path = os.path.join(config.output_directory, json_file)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if 'analysis' in data:
                for mode, analysis in data['analysis'].items():
                    if mode in mode_prompts:
                        if 'result' in analysis and isinstance(analysis['result'], str):
                            mode_prompts[mode].append(analysis['result'])
                        elif 'result' in analysis and isinstance(analysis['result'], dict) and 'caption' in analysis['result']:
                            mode_prompts[mode].append(analysis['result']['caption'])
        except Exception as e:
            logging.error(f"Error processing {json_file}: {str(e)}")
    
    # Write prompts to wildcard txt files
    for mode, prompts in mode_prompts.items():
        if prompts:
            wildcard_file = os.path.join(config.output_directory, f"{mode}_wildcards.txt")
            with open(wildcard_file, 'w') as f:
                f.write("\n".join(prompts))
            logging.info(f"Created wildcard file for {mode}: {wildcard_file}")
    
    logging.info("Finished processing existing JSON files")