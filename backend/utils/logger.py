import logging
import sys
from langchain.callbacks.manager import get_openai_callback

def setup_logger():
    logger = logging.getLogger("defi_assistant")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


def log_with_trace(logger, message, level="info"):
    """Log to console and LangSmith trace if available"""
    try:
        with get_openai_callback() as cb:
            getattr(logger, level)(message)
            # If needed, cb.total_tokens / cb.prompt_tokens can be accessed here
    except Exception:
        getattr(logger, level)(message)
