import os
import logging

def setup_logging(config):
    """
    Setup logging configurations based on the configuration values.

    Args:
        config: Configuration object containing logging settings.

    This function sets up file and console logging, as well as specific loggers for API communication, CLIP API, and LLM API.
    """
    logging.getLogger().handlers.clear()

    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%y %H:%M')
    console_log_format = logging.Formatter('%(message)s')

    if config.log_to_file:
        log_file_path = os.path.join(config.output_directory, config.log_file)
        os.makedirs(config.output_directory, exist_ok=True)
        file_handler = logging.FileHandler(log_file_path, mode=config.log_mode)
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(file_handler)

    if config.log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_log_format)
        console_handler.setLevel(logging.INFO)
        console_handler.setStream(open(1, 'w', encoding='utf-8', closefd=False))
        logging.getLogger().addHandler(console_handler)

    def setup_api_logger(name, log_file):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(os.path.join(config.output_directory, log_file), mode='a', encoding='utf-8')
        handler.setFormatter(log_format)
        logger.addHandler(handler)

    # Set up API logging if enabled
    if config.log_api_communication:
        setup_api_logger('API', 'api_communication.log')

    # Setup CLIP API logger
    setup_api_logger('CLIP_API', 'api_clip.log')

    # Setup LLM API logger
    setup_api_logger('LLM_API', 'api_llm.log')

    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger('PIL').setLevel(logging.WARNING)
