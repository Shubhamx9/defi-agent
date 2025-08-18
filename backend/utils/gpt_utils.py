"""
GPT utility helpers for model selection, cost estimation, and task routing.
Used only when chatbot_settings.USE_GPT = True
"""

from functools import lru_cache
from langchain_openai import ChatOpenAI
from backend.config.settings import openai_settings

# ------------------ Model Configs ------------------
MODEL_CONFIGS = {
    "gpt-5-tiny": {"cost_per_1k_tokens": 0.001, "speed": "ultra-fast", "capabilities": "minimal"},
    "gpt-5-mini": {"cost_per_1k_tokens": 0.003, "speed": "fast", "capabilities": "balanced"},
    "gpt-5": {"cost_per_1k_tokens": 0.01, "speed": "slower", "capabilities": "high reasoning"},
}

TASK_TO_MODEL = {
    "intent": "gpt-5-tiny",
    "query": "gpt-5-mini",
    "action": "gpt-5",
}

# ------------------ GPT Model Loader ------------------
@lru_cache(maxsize=3)
def get_gpt_model(model_name: str):
    """Return a cached LangChain ChatOpenAI instance"""
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Unknown GPT model: {model_name}")

    return ChatOpenAI(
        model=model_name,
        api_key=openai_settings.OPENAI_API_KEY,
        temperature=0,
    )

# ------------------ Heuristics ------------------
def recommend_model_for_task(task_type: str) -> str:
    """Pick the smallest GPT model suitable for task"""
    return TASK_TO_MODEL.get(task_type, "gpt-5-mini")

def estimate_cost(model_name: str, tokens: int) -> float:
    """Estimate cost in USD for a given token usage"""
    if model_name not in MODEL_CONFIGS:
        return 0.0
    return (tokens / 1000) * MODEL_CONFIGS[model_name]["cost_per_1k_tokens"]

def get_model_metadata(model_name: str):
    return MODEL_CONFIGS.get(model_name, {})
