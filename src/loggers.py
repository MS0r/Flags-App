import logging

DEFAULT_LOG_FORMAT = "%(asctime)s - %(filename)s[%(levelname)s]: %(message)s"

LOG = logging.getLogger(__name__)

def setup_basic_logging(level = logging.DEBUG, formatter = None):
    formatter = formatter or DEFAULT_LOG_FORMAT
    streamHandler = logging.StreamHandler()
    logging.basicConfig(format=formatter,handlers=[streamHandler],level=level)
    

    
    