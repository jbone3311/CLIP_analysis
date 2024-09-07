import os
import sys

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import logging
import time
from utils.image_utils import encode_image_to_base64, generate_unique_code
from utils.json_utils import save_json, get_existing_json_files
from utils.api_utils import analyze_image_detailed
from constants import DEFAULTS

def process_clip_images(config, api_url, timeout):
    """
    Process images in a directory and send them for CLIP analysis.

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
        clip_json_output_filename = f"{subdir}_{os.path.splitext(file)[0]}_clip_analysis.json"
        clip_json_full_path = os.path.join(batch_json_dir, clip_json_output_filename)
        
        # Initialize the result dictionary
        detailed_results = {
            'filename': file,
            'unique_code': generate_unique_code(os.path.join(root, file)),
            'directory_name': subdir,
            'model': config.model,
            'prompts': {},
            'analysis': {}
        }

        # Process CLIP analysis only if the JSON file does not exist
        if clip_json_output_filename not in existing_json_files:
            image_counter += 1
            logging.info(f"{file} - {image_counter}/{total_images + len(existing_json_files)}")
            file_path = os.path.join(root, file)
            image_base64 = encode_image_to_base64(file_path)

            if image_base64 is None:
                logging.error(f"Failed to encode image: {file_path}")
                failed_images.append(file_path)
                continue

            # Start timing the processing
            start_time = time.time()

            # Analyze the image in detail
            detailed_results.update(analyze_image_detailed(image_base64, config.model, config.caption_types, api_url, timeout, config))

            # Calculate processing time
            processing_time = time.time() - start_time
            total_processing_time += processing_time

            # Display processing time and estimated remaining time
            average_processing_time = total_processing_time / (image_counter - len(existing_json_files))
            remaining_time = average_processing_time * (total_images + len(existing_json_files) - image_counter)
            logging.info(f"Processing time for {file}: {processing_time:.2f} seconds")
            logging.info(f"Estimated remaining time: {remaining_time:.2f} seconds")

            # Save the combined JSON result
            try:
                save_json(clip_json_full_path, detailed_results)
                logging.info(f"JSON output created: {clip_json_full_path}")
            except Exception as e:
                logging.error(f"Failed to save JSON for {file}: {e}")
                failed_images.append(file_path)

    if failed_images:
        logging.error(f"Failed to process the following images: {failed_images}")

    logging.info("Image processing completed successfully.")
    return failed_images