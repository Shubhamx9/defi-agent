"""
Gemini model management utility for free Google AI models.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config.settings import settings
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
import os

logger = logging.getLogger(__name__)

MODEL_CONFIGS = {
    "gemini-1.5-flash": {
        "cost_per_1k_tokens": {"input": 0.0, "output": 0.0},
        "max_tokens": 8192,
        "capabilities": ["reasoning", "coding", "analysis", "fast_processing"],
        "speed": "very_fast",
        "use_cases": ["general_queries", "intent_classification", "quick_responses"]
    },
    "gemini-1.5-pro": {
        "cost_per_1k_tokens": {"input": 0.0, "output": 0.0},
        "max_tokens": 32768,
        "capabilities": ["advanced_reasoning", "coding", "analysis", "creative"],
        "speed": "medium",
        "use_cases": ["complex_analysis", "advanced_reasoning", "creative_tasks"]
    },
    "gemini-pro": {
        "cost_per_1k_tokens": {"input": 0.0, "output": 0.0},
        "max_tokens": 4096,
        "capabilities": ["reasoning", "coding", "analysis"],
        "speed": "fast",
        "use_cases": ["general_queries", "balanced_performance"]
    }
}

@lru_cache(maxsize=10)
def get_model_instance(
    model_name: str, 
    temperature: float = None, 
    max_tokens: int = None
) -> ChatGoogleGenerativeAI:
    """Get a cached ChatGoogleGenerativeAI instance for the specified model."""
    if not model_name.startswith("gemini"):
        logger.warning(f"Non-Gemini model requested: {model_name}, using gemini-1.5-flash instead")
        model_name = "gemini-1.5-flash"
    
    if temperature is None:
        temperature = settings.DEFAULT_TEMPERATURE
    
    if max_tokens is None:
        model_config = MODEL_CONFIGS.get(model_name, MODEL_CONFIGS["gemini-1.5-flash"])
        max_tokens = model_config.get("max_tokens", settings.MAX_TOKENS)
    
    try:
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    except Exception as e:
        logger.error(f"Failed to create model instance for {model_name}: {e}")
        if model_name != "gemini-1.5-flash":
            logger.info("Falling back to gemini-1.5-flash")
            return get_model_instance("gemini-1.5-flash", temperature, max_tokens)
        raise RuntimeError(f"Model initialization failed: {e}")

def get_intent_model() -> ChatGoogleGenerativeAI:
    """Get model instance for intent classification."""
    return get_model_instance("gemini-1.5-flash", temperature=0)

def get_query_model() -> ChatGoogleGenerativeAI:
    """Get model instance for query processing."""
    return get_model_instance("gemini-1.5-pro", temperature=0)

def get_action_model() -> ChatGoogleGenerativeAI:
    """Get model instance for action extraction."""
    return get_model_instance("gemini-1.5-flash", temperature=0)

def is_model_available(model_name: str) -> bool:
    """Check if a model is available in Google's API."""
    try:
        test_model = ChatGoogleGenerativeAI(
            model=model_name, 
            max_output_tokens=1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        test_model.invoke("test")
        return True
    except Exception as e:
        if "does not exist" in str(e).lower() or "not found" in str(e).lower():
            return False
        logger.warning(f"Could not verify model {model_name}: {e}")
        return False

def get_model_info(model_name: str) -> Dict[str, Any]:
    """Get configuration information for a model."""
    return MODEL_CONFIGS.get(model_name, {
        "cost_per_1k_tokens": {"input": 0.0, "output": 0.0},
        "max_tokens": 4096,
        "capabilities": ["unknown"],
        "speed": "unknown"
    })

def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost for a model call (always 0 for free models)."""
    return 0.0

def recommend_model_for_task(task: str, priority: str = "cost") -> str:
    """Recommend optimal model for a task based on priority."""
    if priority == "cost":
        return "gemini-1.5-flash"  # Always cheapest (free)
    
    elif priority == "speed":
        if task in ["intent", "simple_classification"]:
            return "gemini-1.5-flash"
        else:
            return "gemini-1.5-flash"
    
    elif priority == "capability":
        available_models = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        for model in available_models:
            if is_model_available(model):
                return model
        return "gemini-1.5-flash"
    
    return "gemini-1.5-flash"

def get_optimal_model_config():
    """Get optimal model configuration for different task types."""
    config = {
        "intent": "gemini-1.5-flash",
        "query": "gemini-1.5-pro",
        "action": "gemini-1.5-flash",
        "complex": "gemini-1.5-pro",
        "creative": "gemini-1.5-pro"
    }
    
    for task, model in config.items():
        if not is_model_available(model):
            logger.warning(f"Model {model} not available for {task}, falling back")
            config[task] = "gemini-1.5-flash"
    
    return config

def calculate_cost_savings():
    """Calculate cost analysis for Gemini models (always free)."""
    monthly_usage = {
        "intent_calls": 10000,
        "query_calls": 5000,
        "action_calls": 2000
    }
    
    # All Gemini models are free
    current_cost = 0.0
    gemini_cost = 0.0
    
    model_mapping = {
        "intent_calls": "gemini-1.5-flash",
        "query_calls": "gemini-1.5-pro", 
        "action_calls": "gemini-1.5-flash"
    }
    
    savings = 0.0
    savings_percent = 100.0  # 100% savings with free models
    
    return {
        "current_monthly_cost": round(current_cost, 2),
        "gemini_monthly_cost": round(gemini_cost, 2),
        "monthly_savings": round(savings, 2),
        "savings_percent": round(savings_percent, 1),
        "recommended_config": model_mapping
    }

def upgrade_to_gemini_models():
    """Analyze Gemini benefits and provide recommendations."""
    optimal_config = get_optimal_model_config()
    cost_analysis = calculate_cost_savings()
    
    logger.info("Gemini models available for free usage")
    logger.info("100% cost savings with free Google AI models")
    
    return {
        "available": True,
        "recommended_config": optimal_config,
        "cost_analysis": cost_analysis,
        "upgrade_instructions": {
            "intent": "Use gemini-1.5-flash for ultra-fast free classification",
            "query": "Use gemini-1.5-pro for advanced free reasoning",
            "action": "Use gemini-1.5-flash for fast free parameter extraction",
            "complex": "Use gemini-1.5-pro for complex free analysis"
        }
    }