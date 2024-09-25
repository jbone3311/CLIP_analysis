# directory_processor.py

import os
import subprocess
import logging
from config import Config
from utils import generate_unique_code, setup_logging, save_json, load_json
from db_utils import Database
from typing import Optional
import sys
import io

# Set the console encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class DirectoryProcessor:
    def __init__(self, config: Config):
        self.config = config
        self.db = Database(self.config.database_path) if self.config.use_database else None
        setup_logging(config)
        logging.info(f"{self.config.EMOJI_START} DirectoryProcessor initialized.")

    def process_directory(self):
        logging.info(f"{self.config.EMOJI_INFO} Starting processing of directory: {self.config.image_directory}")
        for root, _, files in os.walk(self.config.image_directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(root, file)
                    unique_id = generate_unique_code(image_path)
                    filename = file
                    date_created = os.path.getctime(image_path)
                    file_size = os.path.getsize(image_path)

                    # Duplicate Check
                    if self.config.use_database:
                        if self.is_processed_db(unique_id):
                            logging.info(f"{self.config.EMOJI_INFO} Skipping already processed (DB): {file}")
                            continue
                        self.db.add_image(unique_id, filename, date_created, file_size)
                        image_id = self.get_image_id_db(unique_id)
                        if image_id is None:
                            logging.error(f"{self.config.EMOJI_ERROR} Failed to retrieve image ID for {file} from DB.")
                            continue

                        self.db.update_image_status(image_id, 'processing')

                    if self.config.use_json:
                        json_path = os.path.join(root, f"{os.path.splitext(file)[0]}.json")
                        if os.path.isfile(json_path):
                            logging.info(f"{self.config.EMOJI_INFO} Skipping already processed (JSON): {file}")
                            continue

                    logging.info(f"{self.config.EMOJI_PROCESSING} Processing image: {file}")

                    try:
                        # Prepare CLIP arguments based on enabled settings
                        clip_args = ['--modes', 'best', 'fast', 'classic', 'negative', 'caption']
                        if self.config.enable_clip_analysis:
                            clip_args.append('--enable-clip-analysis')
                        if self.config.enable_caption:
                            clip_args.append('--enable-caption')
                        if self.config.enable_best:
                            clip_args.append('--enable-best')
                        if self.config.enable_fast:
                            clip_args.append('--enable-fast')
                        if self.config.enable_classic:
                            clip_args.append('--enable-classic')
                        if self.config.enable_negative:
                            clip_args.append('--enable-negative')

                        # Run analysis_interrogate.py with CLIP arguments
                        cmd_interrogate = ['python', 'analysis_interrogate.py', image_path] + clip_args
                        result_interrogate = subprocess.run(
                            cmd_interrogate,
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        json_interrogate = result_interrogate.stdout.strip()
                        if self.config.use_database and self.db:
                            self.db.add_analysis_result(image_id, 'interrogate', None, json_interrogate)
                        if self.config.use_json:
                            with open(json_path, 'w') as f:
                                json.dump({"interrogate": json.loads(json_interrogate)}, f, indent=4)

                        # Run analysis_LLM.py
                        prompts = ','.join([llm['title'] for llm in self.config.llms if self.config.enable_llm_analysis])
                        if prompts:
                            result_llm = subprocess.run(
                                ['python', 'analysis_LLM.py', image_path, '--prompt', prompts, '--model', '1', '--output-to-stdout'],
                                capture_output=True,
                                text=True,
                                check=True
                            )
                            json_llm = result_llm.stdout.strip()
                            if self.config.use_database and self.db:
                                for prompt in [llm['title'] for llm in self.config.llms if self.config.enable_llm_analysis]:
                                    self.db.add_analysis_result(image_id, 'LLM', prompt, json_llm)
                            if self.config.use_json:
                                data = {}
                                if os.path.isfile(json_path):
                                    data = load_json(json_path)
                                data['llm_analysis'] = json.loads(json_llm)
                                with open(json_path, 'w') as f:
                                    json.dump(data, f, indent=4)

                        if self.config.use_database and self.db:
                            self.db.update_image_status(image_id, 'completed')

                        logging.info(f"{self.config.EMOJI_SUCCESS} Successfully processed: {file}")

                    except subprocess.CalledProcessError as e:
                        logging.error(f"{self.config.EMOJI_ERROR} Failed to process {file}: {e.stderr}")
                        if self.config.use_database and self.db and 'image_id' in locals():
                            self.db.update_image_status(image_id, 'failed')
                        continue
                    except Exception as e:
                        logging.error(f"{self.config.EMOJI_ERROR} Unexpected error processing {file}: {e}")
                        if self.config.use_database and self.db and 'image_id' in locals():
                            self.db.update_image_status(image_id, 'failed')
                        continue

        logging.info(f"{self.config.EMOJI_COMPLETE} Directory processing completed.")

    def is_processed_db(self, unique_id: str) -> bool:
        if self.db:
            return self.db.is_processed_db(unique_id)
        return False

    def get_image_id_db(self, unique_id: str) -> Optional[int]:
        if self.db:
            return self.db.get_image_id_db(unique_id)
        return None

    def close(self):
        if self.db:
            self.db.close()
            logging.info(f"{self.config.EMOJI_INFO} Database connection closed.")

if __name__ == "__main__":
    config = Config()
    processor = DirectoryProcessor(config)
    processor.process_directory()
    processor.close()
