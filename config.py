import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

class Config:
    """
    Configuration class for managing application settings.
    Loads settings from environment variables with default values.
    """

    def __init__(self):
        # API Keys
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        self.agentops_api_key = os.getenv('AGENTOPS_API_KEY')

        # API Configuration
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:7860')
        self.timeout = int(os.getenv('TIMEOUT', '60'))  # Increase to 60 seconds or more

        # Directory Settings
        self.image_directory = os.getenv('IMAGE_DIRECTORY', 'path_to_images')
        self.output_directory = os.getenv('OUTPUT_DIRECTORY', 'path_to_output')

        # Logging Configuration
        self.logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
        self.logging_format = os.getenv('LOGGING_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_to_console = os.getenv('LOG_TO_CONSOLE', 'True').lower() == 'true'
        self.log_to_file = os.getenv('LOG_TO_FILE', 'True').lower() == 'true'
        self.log_file = os.getenv('LOG_FILE', 'Log.log')
        self.log_mode = 'w'  # Always overwrite log file
        self.log_api_conversation = os.getenv('LOG_API_CONVERSATION', 'False').lower() == 'true'

        # Model Settings
        self.clip_model_name = os.getenv('CLIP_MODEL_NAME', 'ViT-L-14')
        self.caption_types = os.getenv('CAPTION_TYPES', 'caption,best,fast,classic,negative').split(',')

        # LLM Settings
        self.llm_api_base_url = os.getenv('LLM_API_BASE_URL', 'https://api.openai.com/v1/chat/completions')
        self.llm_model = os.getenv('LLM_MODEL', 'gpt-4')
        self.llm_system_content = os.getenv('LLM_SYSTEM_CONTENT', 'Your default system content here')

        # File Handling Settings
        self.create_individual_files = os.getenv('CREATE_INDIVIDUAL_FILES', 'True').lower() == 'true'
        self.create_prompt_list = os.getenv('CREATE_PROMPT_LIST', 'True').lower() == 'true'
        self.create_master_files = os.getenv('CREATE_MASTER_FILES', 'True').lower() == 'true'
        self.list_file_mode = os.getenv('LIST_FILE_MODE', 'w')
        self.master_analysis_filename = os.getenv('MASTER_ANALYSIS_FILENAME', 'master_analysis.json')
        self.process_json_without_images = os.getenv('PROCESS_JSON_WITHOUT_IMAGES', 'False').lower() == 'true'

        # Image File Extensions
        self.image_file_extensions = os.getenv('IMAGE_FILE_EXTENSIONS', '.png,.jpg,.jpeg').split(',')

        # LLM Configurations
        self.llms = self._load_llm_configs()

        # Analysis Control
        self.clip_enabled = os.getenv('ENABLE_CLIP_ANALYSIS', 'True').lower() == 'true'
        self.llm_enabled = os.getenv('ENABLE_LLM_ANALYSIS', 'False').lower() == 'true'
        self.enable_json_processing = os.getenv('ENABLE_JSON_PROCESSING', 'True').lower() == 'true'

        # Retry Configuration
        self.retry_limit = int(os.getenv('RETRY_LIMIT', '5'))
        self.sleep_interval = int(os.getenv('SLEEP_INTERVAL', '5'))

        # LLM Parameters
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '300'))
        self.top_p = float(os.getenv('TOP_P', '1.0'))
        self.frequency_penalty = float(os.getenv('FREQUENCY_PENALTY', '0.0'))
        self.presence_penalty = float(os.getenv('PRESENCE_PENALTY', '0.0'))

        # Selected Prompts
        self.selected_prompts = [p for p in os.getenv('SELECTED_PROMPTS', '').split(',') if p]

        # New Analysis Modes
        self.enable_caption = os.getenv('ENABLE_CAPTION', 'True').lower() == 'true'
        self.enable_best = os.getenv('ENABLE_BEST', 'True').lower() == 'true'
        self.enable_fast = os.getenv('ENABLE_FAST', 'True').lower() == 'true'
        self.enable_classic = os.getenv('ENABLE_CLASSIC', 'True').lower() == 'true'
        self.enable_negative = os.getenv('ENABLE_NEGATIVE', 'True').lower() == 'true'

        # Additional settings
        self.process_json_to_txt = os.getenv('PROCESS_JSON_TO_TXT', 'True').lower() == 'true'

    def _load_llm_configs(self) -> Dict[str, Dict[str, Any]]:
        llms = {}
        for i in range(1, 5):  # Assuming a maximum of 4 LLM configurations
            enabled = os.getenv(f'LLM_{i}_ENABLED', 'False').lower() == 'true'
            if enabled:
                llms[f'LLM_{i}'] = {
                    'api_url': os.getenv(f'LLM_{i}_API_URL'),
                    'api_key': os.getenv(f'LLM_{i}_API_KEY'),
                }
        return llms

    def get_openai_api_key(self) -> str:
        return self.openai_api_key  # Make sure this attribute is set in the __init__ method

    def get_prompt_options(self, prompt_id: str) -> Dict[str, Any]:
        return {
            'PROMPT_TEXT': os.getenv(f'{prompt_id.upper()}_PROMPT_TEXT', 'Default prompt text'),
            'TEMPERATURE': float(os.getenv(f'{prompt_id.upper()}_TEMPERATURE', str(self.temperature))),
            'MAX_TOKENS': int(os.getenv(f'{prompt_id.upper()}_MAX_TOKENS', str(self.max_tokens)))
        }

    def _get_enabled_modes(self):
        return [mode for mode, enabled in {
            'caption': self.enable_caption,
            'best': self.enable_best,
            'fast': self.enable_fast,
            'classic': self.enable_classic,
            'negative': self.enable_negative
        }.items() if enabled]

    def __str__(self) -> str:
        return f"""
        Configuration:
        - API Base URL: {self.api_base_url}
        - Timeout: {self.timeout}
        - Image Directory: {self.image_directory}
        - Output Directory: {self.output_directory}
        - CLIP Model: {self.clip_model_name}
        - CLIP Mode: {self.clip_mode}
        - LLM Model: {self.llm_model}
        - Enable CLIP Analysis: {self.enable_clip_analysis}
        - Enable LLM Analysis: {self.enable_llm_analysis}
        - Enable JSON Processing: {self.enable_json_processing}
        """