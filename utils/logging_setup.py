import os
import logging

def setup_logging(config):
    """
    Setup logging configurations based on the configuration values.
    """
    log_to_file = config.log_to_file
    log_to_console = config.log_to_console
    log_file = config.log_file
    log_mode = config.log_mode
    output_directory = config.output_directory

    logging.getLogger().handlers.clear()

    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%y %H:%M')
    console_log_format = logging.Formatter('%(message)s')

    if log_to_file:
        log_file_path = os.path.join(output_directory, log_file)
        os.makedirs(output_directory, exist_ok=True)
        file_handler = logging.FileHandler(log_file_path, mode=log_mode, encoding='utf-8')
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(file_handler)

    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_log_format)
        console_handler.setLevel(logging.INFO)
        console_handler.setStream(open(1, 'w', encoding='utf-8', closefd=False))
        logging.getLogger().addHandler(console_handler)

    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger('PIL').setLevel(logging.WARNING)
