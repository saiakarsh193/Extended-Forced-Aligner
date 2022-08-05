import logging

def getLogger(log_path):
    log_format = logging.Formatter('%(asctime)s (%(filename)s:%(lineno)s) [%(levelname)s]: %(message)s')
    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(logging.DEBUG)
    log_file_handler = logging.FileHandler(log_path)
    log_file_handler.setLevel(logging.INFO)
    log_file_handler.setFormatter(log_format)
    logger = logging.getLogger()
    logger.addHandler(log_console_handler)
    logger.addHandler(log_file_handler)
    logger.setLevel(logging.DEBUG)
    return logger
