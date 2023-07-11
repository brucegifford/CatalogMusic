import logging

def setup_logger(logger_name, log_file, level=logging.INFO):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    return logger

def setup_logger2(logger_name, log_file, level=logging.DEBUG, log_file_format = None,
                  console_logging_level = None, console_format = None,
                  error_log_file=None, error_format = None, error_level = logging.ERROR):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    if log_file_format:
        file_formatter = logging.Formatter(log_file_format)
    else:
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(file_formatter)
    logger.addHandler(fileHandler)

    if console_logging_level:
        streamHandler = logging.StreamHandler()
        if console_format:
            console_formatter = logging.Formatter(console_format)
        else:
            console_formatter = logging.Formatter('%(message)s')
        streamHandler.setFormatter(console_formatter)
        streamHandler.setLevel(console_logging_level)
        logger.addHandler(streamHandler)

    if error_log_file:
        errorHandler = logging.FileHandler(error_log_file, mode='w')
        if error_format:
            error_formatter = logging.Formatter(error_format)
        else:
            error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        errorHandler.setFormatter(error_formatter)
        errorHandler.setLevel(error_level)
        logger.addHandler(errorHandler)

    return logger
