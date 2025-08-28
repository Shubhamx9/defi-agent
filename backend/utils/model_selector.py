"""
Unified model selector: GPT-5 (tiny/mini) via API or Local Mistral-7B via Ollama for Testing.
Switch by setting USE_GPT in settings.py
"""

from backend.config.settings import model_settings, chatbot_settings
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama as Ollama
from backend.logging_setup import logger

_MODEL_CACHE = {}

def get_intent_model():
    """Get intent classification model with fallback handling."""
    if chatbot_settings.USE_GPT:
        # Use GPT-5 tiny via API
        model_name = "gpt-5-tiny"
        if model_name not in _MODEL_CACHE:
            try:
                _MODEL_CACHE[model_name] = ChatOpenAI(
                    model_name=model_name,
                    temperature=model_settings.DEFAULT_TEMPERATURE,
                    max_tokens=model_settings.MAX_TOKENS,
                )
                logger.info(f"Loaded intent model: {model_name} (GPT-5 tiny)")
            except Exception as e:
                logger.error(f"Failed to load intent model {model_name}: {e}")
                raise
        return _MODEL_CACHE[model_name]
    else:
        # Use Mistral-7B via Ollama
        model_name = "mistral:7b"
        if model_name not in _MODEL_CACHE:
            try:
                _MODEL_CACHE[model_name] = Ollama(
                    model=model_name,
                    temperature=model_settings.DEFAULT_TEMPERATURE,
                    max_tokens=model_settings.MAX_TOKENS,
                )
                logger.info(f"Loaded intent model: {model_name} (Mistral-7B via Ollama)")
            except Exception as e:
                logger.error(f"Failed to load intent model {model_name}: {e}")
                raise
        return _MODEL_CACHE[model_name]

def tiny_model():
    """Return the appropriate tiny model (GPT-5 Tiny or Mistral-7B via Ollama)."""
    if chatbot_settings.USE_GPT:
        model_name = "gpt-5-tiny"
        if model_name not in _MODEL_CACHE:
            try:
                _MODEL_CACHE[model_name] = ChatOpenAI(
                    model_name=model_name,
                    temperature=model_settings.DEFAULT_TEMPERATURE,
                    max_tokens=model_settings.MAX_TOKENS,
                )
                logger.info(f"Loaded tiny model: {model_name} (GPT-5 Tiny)")
            except Exception as e:
                logger.error(f"Failed to load tiny model {model_name}: {e}")
                raise
        return _MODEL_CACHE[model_name]

    else:
        model_name = "mistral:7b"
        if model_name not in _MODEL_CACHE:
            try:
                _MODEL_CACHE[model_name] = Ollama(
                    model=model_name,
                    temperature=model_settings.DEFAULT_TEMPERATURE,
                    max_tokens=model_settings.MAX_TOKENS,
                )
                logger.info(f"Loaded tiny model: {model_name} (Mistral-7B via Ollama)")
            except Exception as e:
                logger.error(f"Failed to load tiny model {model_name}: {e}")
                raise
        return _MODEL_CACHE[model_name]

def mini_model():
    """Return the appropriate mini model (GPT-5 Mini or Mistral-7B via Ollama)."""
    if chatbot_settings.USE_GPT:
        model_name = "gpt-5-mini"
        if model_name not in _MODEL_CACHE:
            try:
                _MODEL_CACHE[model_name] = ChatOpenAI(
                    model_name=model_name,
                    temperature=model_settings.DEFAULT_TEMPERATURE,
                    max_tokens=model_settings.MAX_TOKENS,
                )
                logger.info(f"Loaded mini model: {model_name} (GPT-5 Mini)")
            except Exception as e:
                logger.error(f"Failed to load mini model {model_name}: {e}")
                raise
        return _MODEL_CACHE[model_name]
    else:
        model_name = "mistral:7b"
        if model_name not in _MODEL_CACHE:
            try:
                _MODEL_CACHE[model_name] = Ollama(
                    model=model_name,
                    temperature=model_settings.DEFAULT_TEMPERATURE,
                    max_tokens=model_settings.MAX_TOKENS,
                )
                logger.info(f"Loaded mini model: {model_name} (Mistral-7B via Ollama)")
            except Exception as e:
                logger.error(f"Failed to load mini model {model_name}: {e}")
                raise
        return _MODEL_CACHE[model_name]
    
