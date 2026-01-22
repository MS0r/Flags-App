import logging
import sys
from logging import Formatter

DEFAULT_LOG_FORMAT = "%(asctime)s - %(filename)s[%(levelname)s]: %(message)s"

def setup_logging(name : str = '',level = logging.DEBUG, format : str | Formatter = None):
    if format is not None:
        if isinstance(format, str):
            formatter = Formatter(format)
        elif isinstance(format, Formatter):
            formatter = format
    else:
        formatter = Formatter(DEFAULT_LOG_FORMAT)
    logger = logging.getLogger(name)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(level)
    logger.addHandler(console)
    logger.setLevel(level)
    return logger