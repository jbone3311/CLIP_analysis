import os
import logging

def setup_logging(config):
    """
    Setup logging configurations based on the configuration values.

    Args:
        config: Configuration object containing logging settings.

    This function sets up file and console logging, as well as specific loggers for API communication, CLIP API, and LLM API.
    """
    log_file = os.path.join(config.output_directory, 'analysis.log')
    os.makedirs(config.output_directory, exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(config.logging_level.upper())  # Use the logging level from config

    # Create handlers
    handlers = []
    if config.log_to_file:
        f_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        f_handler.setLevel(logging.DEBUG)
        handlers.append(f_handler)
    if config.log_to_console:
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        handlers.append(c_handler)

    # Create a consistent formatter with short time format
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Suppress logging from PIL and other noisy libraries
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)  # Suppress urllib3 DEBUG logs

    # Setup API logging
    if config.log_to_file:
        api_logger = logging.getLogger('API')
        api_logger.setLevel(logging.DEBUG)
        api_handler = logging.FileHandler(os.path.join(config.output_directory, 'api_communication.log'), mode='w', encoding='utf-8')
        api_handler.setFormatter(formatter)
        api_logger.addHandler(api_handler)

        # Setup CLIP API logger
        clip_logger = logging.getLogger('CLIP_API')
        clip_logger.setLevel(logging.DEBUG)
        clip_handler = logging.FileHandler(os.path.join(config.output_directory, 'api_clip.log'), mode='w', encoding='utf-8')
        clip_handler.setFormatter(formatter)
        clip_logger.addHandler(clip_handler)

        # Setup LLM API logger if needed
        llm_logger = logging.getLogger('LLM_API')
        llm_logger.setLevel(logging.DEBUG)
        llm_handler = logging.FileHandler(os.path.join(config.output_directory, 'api_llm.log'), mode='w', encoding='utf-8')
        llm_handler.setFormatter(formatter)
        llm_logger.addHandler(llm_handler)
