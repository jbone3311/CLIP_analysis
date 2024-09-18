# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration class for managing application settings.
    Loads settings from environment variables with default values.
    """

    def __init__(self):
        # API Configuration
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:7860')
        self.timeout = int(os.getenv('TIMEOUT', '30'))

        # CLIP Settings
        self.clip_model_name = os.getenv('CLIP_MODEL_NAME', 'ViT-L-14/openai')
        self.enable_clip_analysis = os.getenv('ENABLE_CLIP_ANALYSIS', 'False').lower() == 'true'
        self.enable_caption = os.getenv('ENABLE_CAPTION', 'False').lower() == 'true'
        self.enable_best = os.getenv('ENABLE_BEST', 'False').lower() == 'true'
        self.enable_fast = os.getenv('ENABLE_FAST', 'False').lower() == 'true'
        self.enable_classic = os.getenv('ENABLE_CLASSIC', 'False').lower() == 'true'
        self.enable_negative = os.getenv('ENABLE_NEGATIVE', 'False').lower() == 'true'

        # Processing Settings
        self.process_json_to_txt = os.getenv('PROCESS_JSON_TO_TXT', 'False').lower() == 'true'

        # LLM Settings
        self.enable_llm_analysis = os.getenv('ENABLE_LLM_ANALYSIS', 'False').lower() == 'true'

        # LLM Configurations
        self.llms = []
        for i in range(1, 6):
            title = os.getenv(f'LLM_{i}_TITLE')
            api_url = os.getenv(f'LLM_{i}_API_URL')
            api_key = os.getenv(f'LLM_{i}_API_KEY')
            model = os.getenv(f'LLM_{i}_MODEL', '')
            if title and api_url:
                self.llms.append({
                    'title': title,
                    'api_url': api_url,
                    'api_key': api_key,
                    'model': model
                })

        # General Settings
        self.enable_json_processing = os.getenv('ENABLE_JSON_PROCESSING', 'False').lower() == 'true'
        self.image_directory = os.getenv('IMAGE_DIRECTORY', 'Images')
        self.output_directory = os.getenv('OUTPUT_DIRECTORY', 'Output')
        self.logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
        self.log_api_conversation = os.getenv('LOG_API_CONVERSATION', 'False').lower() == 'true'
        self.retry_limit = int(os.getenv('RETRY_LIMIT', '5'))

        # Duplicate Detection Settings
        self.use_database = os.getenv('USE_DATABASE', 'False').lower() == 'true'
        self.use_json = os.getenv('USE_JSON', 'True').lower() == 'true'

        # Database Configuration
        self.database_path = os.getenv('DATABASE_PATH', 'image_analysis.db')

        # Emojis
        self.EMOJI_SUCCESS = os.getenv('EMOJI_SUCCESS', "✅")
        self.EMOJI_WARNING = os.getenv('EMOJI_WARNING', "⚠️")
        self.EMOJI_ERROR = os.getenv('EMOJI_ERROR', "❌")
        self.EMOJI_INFO = os.getenv('EMOJI_INFO', "ℹ️")
        self.EMOJI_PROCESSING = os.getenv('EMOJI_PROCESSING', "🔄")
        self.EMOJI_START = os.getenv('EMOJI_START', "🚀")
        self.EMOJI_COMPLETE = os.getenv('EMOJI_COMPLETE', "🎉")

        # Logging Format
        self.logging_format = os.getenv('LOGGING_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')
