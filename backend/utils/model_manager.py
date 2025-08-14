"""
Model management utility for OpenAI model configuration and cost optimization.
"""
from langchain_openai import ChatOpenAI
from backend.config.settings import settings
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)

MODEL_CONFIGS = {
    "gpt-5": {
        "cost_per_1k_tokens": {"input": 1.25, "output": 0.125},
        "max_tokens": 10000,
        "capabilities": ["advanced_reasoning", "coding", "analysis", "creative", "multimodal"],
        "speed": "medium",
        "use_cases": ["complex_analysis", "advanced_reasoning", "creative_tasks"]
    },
    "gpt-5-mini": {
        "cost_per_1k_tokens": {"input": 0.25, "output": 0.025},
        "max_tokens": 2000,
        "capabilities": ["reasoning", "coding", "analysis", "fast_processing"],
        "speed": "fast",
        "use_cases": ["general_queries", "action_extraction", "balanced_performance"]
    },
    "gpt-5-nano": {
        "cost_per_1k_tokens": {"input": 0.05, "output": 0.005},
        "max_tokens": 400,
        "capabilities": ["basic_reasoning", "classification", "ultra_fast", "simple_tasks"],
        "speed": "very_fast",
        "use_cases": ["intent_classification", "simple_routing", "quick_responses"]
    },
    "gpt-5-chat-latest": {
        "cost_per_1k_tokens": {"input": 1.25, "output": 0.125},
        "max_tokens": 10000,
        "capabilities": ["advanced_reasoning", "coding", "analysis", "creative", "multimodal", "latest_training"],
        "speed": "medium",
        "use_cases": ["conversational_ai", "latest_features"]
    }
}

@lru_cache(maxsize=10)
def get_model_instance(
    model_name: str, 
    temperature: float = None, 
    max_tokens: int = None
) -> ChatOpenAI:
    """Get a cached ChatOpenAI instance for the specified model."""
    if not model_name.startswith("gpt-5"):
        logger.warning(f"Non-GPT-5 model requested: {model_name}, using gpt-5-mini instead")
        model_name = "gpt-5-mini"
    
    if temperature is None:
        temperature = settings.DEFAULT_TEMPERATURE
    
    if max_tokens is None:
        model_config = MODEL_CONFIGS.get(model_name, MODEL_CONFIGS["gpt-5-mini"])
        max_tokens = model_config.get("max_tokens", settings.MAX_TOKENS)
    
    try:
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            request_timeout=30
        )
    except Exception as e:
        logger.error(f"Failed to create model instance for {model_name}: {e}")
        if model_name != "gpt-5-mini":
            logger.info("Falling back to gpt-5-mini")
            return get_model_instance("gpt-5-mini", temperature, max_tokens)
        raise RuntimeError(f"Model initialization failed: {e}")

def get_intent_model() -> ChatOpenAI:
    """Get model instance for intent classification."""
    return get_model_instance(settings.INTENT_MODEL, temperature=0)

def get_query_model() -> ChatOpenAI:
    """Get model instance for query processing."""
    return get_model_instance(settings.QUERY_MODEL, temperature=0)

def get_action_model() -> ChatOpenAI:
    """Get model instance for action extraction."""
    return get_model_instance(settings.ACTION_MODEL, temperature=0)

def is_model_available(model_name: str) -> bool:
    """Check if a model is available in OpenAI's API."""
    try:
        test_model = ChatOpenAI(model=model_name, max_tokens=1)
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
        "cost_per_1k_tokens": {"input": 0.001, "output": 0.003},
        "max_tokens": 4096,
        "capabilities": ["unknown"],
        "speed": "unknown"
    })

def estimate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost for a model call."""
    model_info = get_model_info(model_name)
    cost_config = model_info.get("cost_per_1k_tokens", {"input": 0.001, "output": 0.003})
    
    input_cost = (input_tokens / 1000) * cost_config["input"]
    output_cost = (output_tokens / 1000) * cost_config["output"]
    
    return input_cost + output_cost

def recommend_model_for_task(task: str, priority: str = "cost") -> str:
    """Recommend optimal model for a task based on priority."""
    if priority == "cost":
        if task in ["intent", "simple_classification"]:
            return "gpt-5-nano"
        elif task in ["simple_query", "basic_reasoning"]:
            return "gpt-5-mini"
        else:
            return "gpt-5-mini"
    
    elif priority == "speed":
        if task in ["intent", "simple_classification"]:
            return "gpt-5-nano"
        else:
            return "gpt-5-mini"
    
    elif priority == "capability":
        available_models = ["gpt-5-chat-latest", "gpt-5", "gpt-5-mini"]
        for model in available_models:
            if is_model_available(model):
                return model
        return "gpt-5-mini"
    
    return settings.DEFAULT_MODEL

def get_optimal_model_config():
    """Get optimal model configuration for different task types."""
    config = {
        "intent": "gpt-5-nano",
        "query": "gpt-5-mini",
        "action": "gpt-5-mini",
        "complex": "gpt-5",
        "creative": "gpt-5-chat-latest"
    }
    
    for task, model in config.items():
        if not is_model_available(model):
            logger.warning(f"Model {model} not available for {task}, falling back")
            if task == "intent":
                config[task] = "gpt-5-mini"
            elif task in ["query", "action"]:
                config[task] = "gpt-5-mini"
            else:
                config[task] = "gpt-5"
    
    return config

def calculate_cost_savings():
    """Calculate cost analysis for GPT-5 model optimization."""
    monthly_usage = {
        "intent_calls": 10000,
        "query_calls": 5000,
        "action_calls": 2000
    }
    
    avg_tokens = {
        "intent": {"input": 50, "output": 5},
        "query": {"input": 200, "output": 150},
        "action": {"input": 100, "output": 50}
    }
    
    # Baseline cost calculation
    current_cost = 0
    baseline_cost = {"input": 0.00015, "output": 0.0006}
    
    for task, calls in monthly_usage.items():
        tokens = avg_tokens[task.replace("_calls", "")]
        input_cost = (calls * tokens["input"] / 1000) * baseline_cost["input"]
        output_cost = (calls * tokens["output"] / 1000) * baseline_cost["output"]
        current_cost += input_cost + output_cost
    
    gpt5_cost = 0
    model_mapping = {
        "intent_calls": "gpt-5-nano",
        "query_calls": "gpt-5-mini", 
        "action_calls": "gpt-5-mini"
    }
    
    for task, calls in monthly_usage.items():
        model = model_mapping[task]
        model_cost = MODEL_CONFIGS[model]["cost_per_1k_tokens"]
        tokens = avg_tokens[task.replace("_calls", "")]
        
        input_cost = (calls * tokens["input"] / 1000) * model_cost["input"]
        output_cost = (calls * tokens["output"] / 1000) * model_cost["output"]
        gpt5_cost += input_cost + output_cost
    
    savings = current_cost - gpt5_cost
    savings_percent = (savings / current_cost) * 100 if current_cost > 0 else 0
    
    return {
        "current_monthly_cost": round(current_cost, 2),
        "gpt5_monthly_cost": round(gpt5_cost, 2),
        "monthly_savings": round(savings, 2),
        "savings_percent": round(savings_percent, 1),
        "recommended_config": model_mapping
    }

def upgrade_to_gpt5_models():
    """Analyze GPT-5 upgrade benefits and provide recommendations."""
    optimal_config = get_optimal_model_config()
    cost_analysis = calculate_cost_savings()
    
    logger.info("GPT-5 models available for upgrade")
    logger.info(f"Potential monthly savings: ${cost_analysis['monthly_savings']} ({cost_analysis['savings_percent']}%)")
    
    return {
        "available": True,
        "recommended_config": optimal_config,
        "cost_analysis": cost_analysis,
        "upgrade_instructions": {
            "intent": "Switch to gpt-5-nano for significant cost reduction",
            "query": "Switch to gpt-5-mini for improved performance",
            "action": "Switch to gpt-5-mini for better parameter extraction",
            "complex": "Use gpt-5 for advanced reasoning tasks"
        }
    }