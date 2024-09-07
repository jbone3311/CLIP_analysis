import logging
import os
import configparser
from constants import DEFAULTS

def mask_api_key(api_key):
    """Mask the API key for secure logging."""
    if len(api_key) < 6:
        return "*" * len(api_key)
    return api_key[:3] + "*" * (len(api_key) - 6) + api_key[-3:]

class Config:
    """
    Configuration handler to load and manage application settings.
    """

    def __init__(self, config_file='config.ini'):
        self.config_file = config_file
        self.config = configparser.RawConfigParser()
        self.load_config()

    def load_config(self):
        """
        Load configuration from the config file.
        """
        if not os.path.exists(self.config_file):
            self.create_default_config()
        self.config.read(self.config_file)

        # General Settings
        self.image_directory = self.config.get('DEFAULT', 'IMAGE_DIRECTORY', fallback=DEFAULTS['DEFAULT']['IMAGE_DIRECTORY'])
        self.output_directory = self.config.get('DEFAULT', 'OUTPUT_DIRECTORY', fallback=DEFAULTS['DEFAULT']['OUTPUT_DIRECTORY'])
        self.api_base_url = self.config.get('DEFAULT', 'API_BASE_URL', fallback=DEFAULTS['DEFAULT']['API_BASE_URL'])
        self.api_key = self.get_openai_api_key()
        self.timeout = self.config.getint('DEFAULT', 'TIMEOUT', fallback=DEFAULTS['DEFAULT']['TIMEOUT'])

        # Logging Settings
        self.logging_level = self.config.get('DEFAULT', 'LOGGING_LEVEL', fallback=DEFAULTS['DEFAULT']['LOGGING_LEVEL'])
        self.logging_format = self.config.get('DEFAULT', 'LOGGING_FORMAT', fallback=DEFAULTS['DEFAULT']['LOGGING_FORMAT'])
        self.log_to_console = self.config.getboolean('DEFAULT', 'LOG_TO_CONSOLE', fallback=DEFAULTS['DEFAULT']['LOG_TO_CONSOLE'])
        self.log_to_file = self.config.getboolean('DEFAULT', 'LOG_TO_FILE', fallback=DEFAULTS['DEFAULT']['LOG_TO_FILE'])
        self.log_file = self.config.get('DEFAULT', 'LOG_FILE', fallback=DEFAULTS['DEFAULT']['LOG_FILE'])
        self.log_mode = self.config.get('DEFAULT', 'LOG_MODE', fallback=DEFAULTS['DEFAULT']['LOG_MODE'])
        self.log_api_communication = self.config.getboolean('DEFAULT', 'LOG_API_COMMUNICATION', fallback=DEFAULTS['DEFAULT']['LOG_API_COMMUNICATION'])

        # File Handling Settings
        self.create_individual_files = self.config.getboolean('DEFAULT', 'CREATE_INDIVIDUAL_FILES', fallback=DEFAULTS['DEFAULT']['CREATE_INDIVIDUAL_FILES'])
        self.create_prompt_list = self.config.getboolean('DEFAULT', 'CREATE_PROMPT_LIST', fallback=DEFAULTS['DEFAULT']['CREATE_PROMPT_LIST'])
        self.create_master_files = self.config.getboolean('DEFAULT', 'CREATE_MASTER_FILES', fallback=DEFAULTS['DEFAULT']['CREATE_MASTER_FILES'])
        self.list_file_mode = self.config.get('DEFAULT', 'LIST_FILE_MODE', fallback=DEFAULTS['DEFAULT']['LIST_FILE_MODE'])

        # Model Settings
        self.model = self.config.get('DEFAULT', 'MODEL', fallback=DEFAULTS['DEFAULT']['MODEL'])
        self.model_nickname = self.config.get('DEFAULT', 'MODEL_NICKNAME', fallback=self.model)
        self.caption_types = self.get_config_list('CAPTION_TYPES')

        # Filename-related variables
        self.master_analysis_filename = self.config.get('DEFAULT', 'MASTER_ANALYSIS_FILENAME', fallback=DEFAULTS['DEFAULT']['MASTER_ANALYSIS_FILENAME'])

        # New option for processing JSON files without images
        self.process_json_without_images = self.config.getboolean('DEFAULT', 'PROCESS_JSON_WITHOUT_IMAGES', fallback=DEFAULTS['DEFAULT']['PROCESS_JSON_WITHOUT_IMAGES'])

        # LLM Settings
        self.selected_prompts = self.get_config_list('SELECTED_PROMPT')
        self.llm_system_content = self.config.get('DEFAULT', 'LLM_SYSTEM_CONTENT', fallback=DEFAULTS['DEFAULT']['LLM_SYSTEM_CONTENT'])
        self.llm_model = self.config.get('DEFAULT', 'LLM_MODEL', fallback=DEFAULTS['DEFAULT']['LLM_MODEL'])

        # Multiple LLMs configuration
        self.llms = {}
        for i in range(2, 5):  # Assuming we have up to 4 LLMs, with OpenAI hardcoded as the first
            llm_key = f'LLM_{i}'
            if self.config.has_section(llm_key):
                self.llms[llm_key] = {
                    'enabled': self.config.getboolean(llm_key, 'ENABLED', fallback=False),
                    'api_url': self.config.get(llm_key, 'API_URL', fallback=''),
                    'api_key': self.config.get(llm_key, 'API_KEY', fallback='')
                }
                logging.debug("LLM configuration for %s: %s" % (llm_key, self.llms[llm_key]))

    def get_config_list(self, key):
        """
        Get a list of values from a comma-separated config entry.

        :param key: Configuration key.
        :return: List of values.
        """
        return [item.strip() for item in self.config.get('DEFAULT', key, fallback='').split(',')]

    def create_default_config(self):
        """
        Create a default configuration file if it does not exist.
        """
        with open(self.config_file, 'w', encoding='utf-8') as configfile:
            for section, options in DEFAULTS.items():
                configfile.write(f"[{section}]\n")
                for key, value in options.items():
                    configfile.write(f"{key} = {value}\n")
                configfile.write("\n")
        self.config.read(self.config_file)

    def get_openai_api_key(self):
        """
        Get the OpenAI API key from the environment variable.
        """
        api_key = os.getenv('OPENAI_API_KEY', '')
        if not api_key:
            logging.error("OpenAI API Key not found in environment.")
        logging.debug(f"Fetched OpenAI API Key: {mask_api_key(api_key)}")
        return api_key