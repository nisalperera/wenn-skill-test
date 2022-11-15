import sys
import logging


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("gunicorn.error")

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('logs/debug-logs.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    return logger
