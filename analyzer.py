import os
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Set, List

class Analyzer(ABC):
    """
    Abstract base class for image analyzers.
    
    This class provides a common structure for different types of image analyzers,
    including methods for processing directories, handling existing files, and
    saving results. Subclasses should implement the `analyze_image` method.
    """

    def __init__(self, directory: str):
        self.directory = directory
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @abstractmethod
    def analyze_image(self, image_path: str) -> Dict:
        pass

    def get_existing_json_files(self) -> Set[str]:
        existing_files = set()
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith('.json'):
                    existing_files.add(file)
        return existing_files

    def process_directory(self) -> None:
        start_time = time.time()
        existing_files = self.get_existing_json_files()
        total_images = sum(len(files) for _, _, files in os.walk(self.directory) 
                           if any(f.lower().endswith(('.png', '.jpg', '.jpeg')) for f in files))
        processed_images = 0

        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(root, file)
                    if self.should_process_file(file, existing_files):
                        try:
                            result = self.analyze_image(image_path)
                            self.save_result(image_path, result)
                            processed_images += 1
                            logging.info(f"Processed {processed_images}/{total_images}: {file}")
                        except Exception as e:
                            logging.error(f"Error processing {image_path}: {e}")

        total_time = time.time() - start_time
        logging.info(f"Total processing time: {total_time:.2f} seconds")
        logging.info(f"Processed {processed_images}/{total_images} images")

    def save_result(self, image_path: str, result: Dict) -> None:
        json_path = f"{os.path.splitext(image_path)[0]}_{self.__class__.__name__}.json"
        self.ensure_output_directory(os.path.dirname(json_path))
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2)
        logging.info(f"Saved results to {json_path}")

    def should_process_file(self, file: str, existing_files: Set[str]) -> bool:
        json_filename = f"{os.path.splitext(file)[0]}_{self.__class__.__name__}.json"
        if json_filename in existing_files:
            logging.info(f"Skipping {file}, JSON already exists.")
            return False
        return True

    def ensure_output_directory(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def get_image_files(self) -> List[str]:
        image_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.lower().endswith(tuple(self.config.image_file_extensions)):
                    image_files.append(os.path.join(root, file))
        return image_files
