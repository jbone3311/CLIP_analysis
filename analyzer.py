import os
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
from image_utils import generate_unique_code
import json_utils

class Analyzer(ABC):
    def __init__(self, directory: str):
        self.directory = directory
        self.image_extensions: Tuple[str, ...] = ('.jpg', '.jpeg', '.png')

    @abstractmethod
    def analyze_image(self, image_path: str) -> Dict:
        pass

    def process_directory(self) -> None:
        start_time = time.time()
        existing_files = self.get_existing_json_files()

        total_images, processed_images = self._process_images(existing_files)

        self._log_processing_summary(total_images, processed_images, start_time)

    def _process_images(self, existing_files: List[str]) -> Tuple[int, int]:
        total_images, processed_images = 0, 0

        for image_path in self.get_image_files():
            total_images += 1
            if json_utils.should_process_file(image_path, existing_files, self.__class__.__name__):
                try:
                    result = self.analyze_image(image_path)
                    self.save_result(image_path, result)
                    processed_images += 1
                    logging.info(f"Processed {processed_images}/{total_images}: {os.path.basename(image_path)}")
                except Exception as e:
                    logging.error(f"Error processing {image_path}: {e}")

        return total_images, processed_images

    def _log_processing_summary(self, total_images: int, processed_images: int, start_time: float) -> None:
        total_time = time.time() - start_time
        logging.info(f"Total processing time: {total_time:.2f} seconds")
        logging.info(f"Processed {processed_images}/{total_images} images")

    def save_result(self, image_path: str, result: Dict) -> None:
        json_path = f"{os.path.splitext(image_path)[0]}_{self.__class__.__name__}.json"
        self.ensure_output_directory(os.path.dirname(json_path))
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2)
        logging.info(f"Saved results to {json_path}")

    def ensure_output_directory(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def get_image_files(self) -> List[str]:
        image_files = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.lower().endswith(self.image_extensions):
                    image_files.append(os.path.join(root, file))
        return image_files

    def get_existing_json_files(self) -> List[str]:
        return json_utils.get_existing_json_files(self.directory)
