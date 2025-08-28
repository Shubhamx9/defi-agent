# logging_setup.py
import logging
import os
from logging.handlers import TimedRotatingFileHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'app.log')

def setup_logger(name: str = "app"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d] - %(message)s'
    )

    file_handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=7)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# ✅ Global logger available for import
logger = setup_logger()
