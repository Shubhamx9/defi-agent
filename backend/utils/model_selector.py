"""
Model selector that seamlessly switches between GPT-5 and Gemini systems.
"""
from backend.config.settings import settings

# Seamless switching based on USE_GEMINI setting
if settings.USE_GEMINI:
    # Use free Gemini models
    from backend.utils.gemini_manager import (
        get_model_instance,
        get_intent_model,
        get_query_model,
        get_action_model,
        is_model_available,
        get_model_info,
        estimate_cost,
        recommend_model_for_task,
        get_optimal_model_config,
        calculate_cost_savings,
        upgrade_to_gemini_models as get_upgrade_info,
        MODEL_CONFIGS
    )
else:
    # Use paid GPT-5 models
    from backend.utils.gpt_manager import (
        get_model_instance,
        get_intent_model,
        get_query_model,
        get_action_model,
        is_model_available,
        get_model_info,
        estimate_cost,
        recommend_model_for_task,
        get_optimal_model_config,
        calculate_cost_savings,
        upgrade_to_gpt5_models as get_upgrade_info,
        MODEL_CONFIGS
    )

def get_current_system_info():
    """Get information about the currently active model system."""
    if settings.USE_GEMINI:
        return {
            "system": "Gemini",
            "provider": "Google",
            "cost": "Free",
            "models": list(MODEL_CONFIGS.keys()),
            "primary_model": "gemini-1.5-flash"
        }
    else:
        return {
            "system": "GPT-5",
            "provider": "OpenAI", 
            "cost": "Paid",
            "models": list(MODEL_CONFIGS.keys()),
            "primary_model": "gpt-5-mini"
        }

def switch_to_gemini():
    """Instructions to switch to Gemini system."""
    return {
        "instruction": "Set USE_GEMINI = True in settings.py",
        "benefits": ["100% free", "No API costs", "Good performance"],
        "requirements": ["GOOGLE_API_KEY environment variable"]
    }

def switch_to_gpt():
    """Instructions to switch to GPT system."""
    return {
        "instruction": "Set USE_GEMINI = False in settings.py", 
        "benefits": ["Latest GPT-5 models", "Advanced capabilities", "Optimized costs"],
        "requirements": ["OPENAI_API_KEY environment variable", "Paid OpenAI account"]
    }