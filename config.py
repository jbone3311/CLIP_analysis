import os
from dotenv import load_dotenv

load_dotenv()

def mask_api_key(api_key):
    """Mask the API key for secure logging."""
    if len(api_key) < 6:
        return "*" * len(api_key)
    return api_key[:3] + "*" * (len(api_key) - 6) + api_key[-3:]

class Config:
    """
    Configuration handler to load and manage application settings.
    """

    def __init__(self):
        self.load_config()

    def load_config(self):
        """
        Load configuration from environment variables.
        """
        # API Keys
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        self.openai_api_key = self.get_openai_api_key()
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_cse_id = os.getenv('GOOGLE_CSE_ID')
        self.agentops_api_key = os.getenv('AGENTOPS_API_KEY')

        # Local LLM Settings
        self.local_llm_model_path = os.getenv('LOCAL_LLM_MODEL_PATH')
        self.openai_api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        self.openai_model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo')

        # API Configuration
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:5000')
        self.timeout = int(os.getenv('TIMEOUT', '40'))

        # Directory Settings
        self.image_directory = os.getenv('IMAGE_DIRECTORY', 'Images')
        self.output_directory = os.getenv('OUTPUT_DIRECTORY', 'Output')

        # Logging Configuration
        self.logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
        self.logging_format = os.getenv('LOGGING_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_to_console = os.getenv('LOG_TO_CONSOLE', 'True').lower() == 'true'
        self.log_to_file = os.getenv('LOG_TO_FILE', 'True').lower() == 'true'
        self.log_file = os.getenv('LOG_FILE', 'image_analysis.log')
        self.log_mode = os.getenv('LOG_MODE', 'a')
        self.log_api_communication = os.getenv('LOG_API_COMMUNICATION', 'False').lower() == 'true'

        # Model Settings
        self.model = os.getenv('MODEL', 'ViT-g-14/laion2B-s34B-b88K')
        self.caption_types = os.getenv('CAPTION_TYPES', 'caption,best,fast,classic,negative').split(',')

        # LLM Settings
        self.llm_api_base_url = os.getenv('LLM_API_BASE_URL', 'https://api.openai.com/v1/chat/completions')
        self.llm_model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        self.llm_system_content = os.getenv('LLM_SYSTEM_CONTENT', 'You are a helpful assistant.')

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
        self.llms = {}
        for i in range(1, 5):
            enabled = os.getenv(f'LLM_{i}_ENABLED', 'False').lower() == 'true'
            if enabled:
                self.llms[f'LLM_{i}'] = {
                    'enabled': enabled,
                    'api_url': os.getenv(f'LLM_{i}_API_URL', ''),
                    'api_key': os.getenv(f'LLM_{i}_API_KEY', '')
                }

        # Selected Prompts
        self.selected_prompts = os.getenv('SELECTED_PROMPTS', 'default').split(',')

        # LLM-specific configuration options
        self.top_p = float(os.getenv('TOP_P', '1.0'))
        self.frequency_penalty = float(os.getenv('FREQUENCY_PENALTY', '0.0'))
        self.presence_penalty = float(os.getenv('PRESENCE_PENALTY', '0.0'))

    def get_openai_api_key(self):
        """
        Get the OpenAI API key from the environment variable.
        """
        api_key = os.getenv('OPENAI_API_KEY', '')
        if not api_key:
            raise ValueError("OpenAI API Key not found in environment.")
        return api_key

    def get_prompt_options(self, prompt_id):
        """
        Get prompt options for a given prompt ID.
        """
        # This is a placeholder implementation. You should replace this with your actual prompt options logic.
        return {
            'PROMPT_TEXT': f'Default prompt text for {prompt_id}',
            'TEMPERATURE': 0.7,
            'MAX_TOKENS': 150
        }

    def __str__(self):
        """
        Return a string representation of the configuration, masking sensitive data.
        """
        return f"""
        Configuration:
        - Image Directory: {self.image_directory}
        - Output Directory: {self.output_directory}
        - API Base URL: {self.api_base_url}
        - OpenAI API Key: {mask_api_key(self.openai_api_key)}
        - Timeout: {self.timeout}
        - Logging Level: {self.logging_level}
        - Model: {self.model}
        - Caption Types: {', '.join(self.caption_types)}
        - LLM Model: {self.llm_model}
        - Create Individual Files: {self.create_individual_files}
        - Create Master Files: {self.create_master_files}
        - Image File Extensions: {', '.join(self.image_file_extensions)}
        """