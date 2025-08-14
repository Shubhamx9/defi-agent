import json
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from backend.utils.cache import get_cached_response, set_cached_response
from backend.models.schemas import ActionExtractionResult, DeFiAction
from backend.utils.model_selector import get_action_model
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)

def _get_action_model():
    """Get action extraction model with fallback handling."""
    return get_action_model()

_action_prompt = ChatPromptTemplate.from_template(
    """Extract structured DeFi action details from the user's request.
Return STRICT JSON only (no prose) with keys:
- action: one of ["deposit","withdraw","swap","stake","borrow","lend","unstake","claim_rewards"]
- amount: number or null (numeric amount only, no currency symbol)
- asset: string or null
- protocol: string or null
- chain: string or null
- apy_min: number or null
- apy_max: number or null
- slippage: number or null
- notes: string or null
- recipient: string or null
- duration: number or null

If a value is not specified, use null.
User: {query}"""
)

SESSION_TTL = 300  # 5 minutes


def _get_default_action_state() -> ActionExtractionResult:
    """Get default action state with proper schema."""
    return ActionExtractionResult()


def _merge_action_results(old: ActionExtractionResult, new: ActionExtractionResult) -> ActionExtractionResult:
    """Merge new action details into old, preferring new values if present."""
    merged_data = old.dict()
    new_data = new.dict()
    
    for key, value in new_data.items():
        if value is not None:
            merged_data[key] = value
    
    return ActionExtractionResult(**merged_data)


@traceable(name="DeFi Action Extraction")
def extract_action_details(user_query: str, user_id: str) -> ActionExtractionResult:
    """
    Extract DeFi action details and merge with existing session state in Redis.
    Returns properly validated ActionExtractionResult schema.
    """
    # Step 1: Load existing session state (if any)
    cache_key = f"action_session:{user_id}"
    cached_state_json = get_cached_response(cache_key)
    
    if cached_state_json:
        try:
            cached_data = json.loads(cached_state_json)
            session_state = ActionExtractionResult(**cached_data)
        except (json.JSONDecodeError, ValueError):
            session_state = _get_default_action_state()
    else:
        session_state = _get_default_action_state()

    # Step 2: Extract new details
    action_model = _get_action_model()
    msg = _action_prompt.format_messages(query=user_query)
    raw_output = action_model.invoke(msg).content.strip()

    try:
        new_data = json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            new_data = json.loads(cleaned)
        except Exception:
            new_data = {}

    # Step 3: Create new result with validation
    try:
        # Map action string to enum if present
        if "action" in new_data and new_data["action"]:
            try:
                new_data["action"] = DeFiAction(new_data["action"].lower())
            except ValueError:
                # Invalid action, keep as None
                new_data["action"] = None
        
        new_result = ActionExtractionResult(**new_data)
    except ValueError:
        # If validation fails, return current session state
        new_result = _get_default_action_state()

    # Step 4: Merge with session state
    final_result = _merge_action_results(session_state, new_result)

    # Step 5: Save updated session state back to Redis with TTL
    set_cached_response(cache_key, json.dumps(final_result.dict()), ttl=SESSION_TTL)

    return final_result


# Backward compatibility function
def extract_action_details_dict(user_query: str, user_id: str) -> Dict[str, Any]:
    """Backward compatibility wrapper that returns dict instead of schema."""
    result = extract_action_details(user_query, user_id)
    result_dict = result.dict()
    
    # Convert enum back to string for backward compatibility
    if result_dict.get("action"):
        result_dict["action"] = result_dict["action"].value
    
    return result_dict
