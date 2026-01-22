import logging
import sys

DEFAULT_LOG_FORMAT = "%(asctime)s - %(filename)s[%(levelname)s]: %(message)s"

def setup_logging(name : str = '',level = logging.DEBUG, formatter = None):
    formatter = formatter or logging.Formatter(DEFAULT_LOG_FORMAT)
    logger = logging.getLogger(name)
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    console.setLevel(level)
    logger.addHandler(console)
    logger.setLevel(level)
    return logger