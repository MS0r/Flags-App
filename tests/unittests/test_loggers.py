import logging
import re
from flags.loggers import setup_logging

def test_setup_logging_creates_logger():
    name = "test_logger_unique"
    
    logger = setup_logging(name, level=logging.INFO)
    assert logger.level == logging.INFO
    assert len(logger.handlers) >= 1
    assert logger.handlers[0].formatter is not None

def test_logger_info(caplog):
    name = "test_logger_info"
    formatter = "%(asctime)s - [%(levelname)s]: %(message)s"

    logger = setup_logging(name, level=logging.INFO,format=formatter)
    logger.info("test")
    assert any('test' in rec.message for rec in caplog.records)

    pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+ - \[INFO\]: test$')
    assert any(pattern.match(logger.handlers[0].formatter.format(rec)) for rec in caplog.records)