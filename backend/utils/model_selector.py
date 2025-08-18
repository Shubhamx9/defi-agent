"""
Unified model selector: GPT-5 (tiny/mini/main) via API or Local Mistral-7B via Ollama.
Switch by setting USE_GPT in settings.py
"""

from backend.config.settings import chatbot_settings
from backend.utils import gpt_utils
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama

_MODEL_CACHE = {}

# ------------------ GPT (API via LangChain) ------------------
def _get_gpt_model(task="main"):
    model_name = gpt_utils.recommend_model_for_task(task)
    return gpt_utils.get_gpt_model(model_name), model_name

# ------------------ Mistral (Local via Ollama + LangChain) ------------------
def _get_mistral_model():
    from langchain_community.chat_models import ChatOllama
    if "mistral" not in _MODEL_CACHE:
        _MODEL_CACHE["mistral"] = ChatOllama(model="mistral:7b", temperature=0)
    return _MODEL_CACHE["mistral"]

def get_query_model(task="main"):
    """
    Returns a LangChain chat model instance based on task:
    - "tiny" | "mini" | "main" for GPT (via API)
    - mistral:7b if USE_GPT = False
    """
    if chatbot_settings.USE_GPT:
        model, _ = _get_gpt_model(task)
        return model
    else:
        return _get_mistral_model()

def get_action_model(task="main"):
    """
    Returns a LangChain chat model instance for action generation:
    - "tiny" | "mini" | "main" for GPT (via API)
    - mistral:7b if USE_GPT = False
    """
    if chatbot_settings.USE_GPT:
        model, _ = _get_gpt_model(task)
        return model
    else:
        return _get_mistral_model()


# Cache to avoid reloading models
_model_cache = {}

def get_intent_model():
    """
    Returns the model for intent classification:
    - GPT-5 Tiny if USE_GPT = True
    - Mistral 7B via Ollama if USE_GPT = False
    """
    global _model_cache
    if "intent_model" in _model_cache:
        return _model_cache["intent_model"]

    if chatbot_settings.USE_GPT:
        # OpenAI GPT tiny model
        model = ChatOpenAI(
            model="gpt-5-tiny",
            temperature=0,
            max_tokens=64
        )
    else:
        # Local Ollama mistral 7b
        model = ChatOllama(
            model="mistral:7b",
            temperature=0,
            num_ctx=2048
        )

    _model_cache["intent_model"] = model
    return model

# ------------------ Main Unified Ask Function ------------------
def ask_model(prompt, task="main", system_prompt=None):
    """
    Query GPT (tiny/mini/main) or Mistral depending on settings.
    task = "tiny" | "mini" | "main"
    """

    if chatbot_settings.USE_GPT:
        model, model_name = _get_gpt_model(task)
        resp = model.invoke(
            [
                {"role": "system", "content": system_prompt or "You are an AI assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        return resp.content.strip(), {"model": model_name, "cost_estimate": gpt_utils.estimate_cost(model_name, len(prompt.split()))}

    else:
        model = _get_mistral_model()
        resp = model.invoke(
            [
                {"role": "system", "content": system_prompt or "You are an AI assistant."},
                {"role": "user", "content": prompt},
            ]
        )
        return resp.content.strip(), {"model": "mistral:7b", "cost_estimate": 0.0}

def get_current_system_info():
    if chatbot_settings.USE_GPT:
        return {
            "system": "GPT-5 (API via OpenAI)",
            "models": list(gpt_utils.MODEL_CONFIGS.keys()),
            "costs": gpt_utils.MODEL_CONFIGS,
        }
    else:
        return {
            "system": "Mistral-7B (local Ollama)",
            "model": "mistral:7b",
            "cost": "Free (local resources)",
        }

def clear_model_cache():
    _MODEL_CACHE.clear()
    gpt_utils.get_gpt_model.cache_clear()
