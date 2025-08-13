# Logging setup
import logging
import sys

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Silence overly verbose logs from libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)

    return logger
