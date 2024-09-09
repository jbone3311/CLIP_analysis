import os
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Iterator
from image_utils import generate_unique_code
import json_utils

class Analyzer(ABC):
    def __init__(self, config):
        self.config = config
        self.directory = config.image_directory
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enabled_modes = self._get_enabled_modes()

    @abstractmethod
    def _get_enabled_modes(self) -> List[str]:
        pass

    @abstractmethod
    def analyze_image(self, image_path: str, modes: List[str]) -> Dict[str, Any]:
        pass

    def get_image_files(self) -> Iterator[str]:
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.lower().endswith(tuple(self.config.image_file_extensions)):
                    yield os.path.join(root, file)

    def process_images(self):
        for image_path in self.get_image_files():
            json_path = os.path.splitext(image_path)[0] + f"_{self.__class__.__name__}.json"
            if json_utils.should_process_file(image_path, json_path, self.__class__.__name__, self.config):
                result = self.analyze_image(image_path, self.enabled_modes)
                if result:  # Only save if result is not None
                    self.save_result(json_path, result)

    def save_result(self, json_path: str, result: Dict[str, Any]):
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=4)
        self.logger.info(f"Saved results to {json_path}")

    def _get_file_info(self, image_path: str) -> Dict[str, Any]:
        return {
            'filename': os.path.basename(image_path),
            'folder': os.path.relpath(os.path.dirname(image_path), self.directory),
            'unique_hash': generate_unique_code(image_path),
            'date_created': os.path.getctime(image_path),
            'date_processed': time.time(),
            'file_size': os.path.getsize(image_path)
        }
