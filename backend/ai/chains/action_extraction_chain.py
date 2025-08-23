import json
from typing import Dict, Any
from langchain.prompts import ChatPromptTemplate
from backend.utils.cache import get_cached_response, set_cached_response
from backend.models.schemas import ActionExtractionResult, DeFiAction
from backend.utils.model_selector import get_action_model
from langsmith import traceable
import logging

logger = logging.getLogger(__name__)

# Prompt for extracting structured action info
_action_prompt = ChatPromptTemplate.from_template(
    """Current: {current_state}
User: {query}

Extract JSON only. Do NOT add any text outside JSON.

- action: one of ["deposit","withdraw","swap","stake","borrow","lend","unstake","claim_rewards"] or null
- amount: numeric value only, or null
- token_in: token symbol (e.g., "ETH", "USDC") or null  
- token_out: token symbol or null
- protocol: string or null
- slippage: numeric value or null

Only extract info from this message. Do not infer from prior context. Return strictly valid JSON."""
)


SESSION_TTL = 300  # 5 minutes


def _get_default_action_state() -> ActionExtractionResult:
    """Get default action state with proper schema."""
    return ActionExtractionResult()


def _format_current_state(session_state: ActionExtractionResult) -> str:
    """Format current transaction state for AI context."""
    state_dict = session_state.dict()
    filled_fields = {k: v for k, v in state_dict.items() if v is not None}
    
    if not filled_fields:
        return "No transaction details collected yet."
    
    summary_parts = []
    if filled_fields.get("action"):
        summary_parts.append(f"Action: {filled_fields['action']}")
    if filled_fields.get("amount"):
        summary_parts.append(f"Amount: {filled_fields['amount']}")
    if filled_fields.get("token_in"):
        summary_parts.append(f"From token: {filled_fields['token_in']}")
    if filled_fields.get("token_out"):
        summary_parts.append(f"To token: {filled_fields['token_out']}")
    if filled_fields.get("protocol"):
        summary_parts.append(f"Protocol: {filled_fields['protocol']}")
    if filled_fields.get("slippage"):
        summary_parts.append(f"Slippage: {filled_fields['slippage']}%")
    
    return "Current transaction: " + ", ".join(summary_parts)


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


    # Step 2: Extract new details with context awareness
    action_model = get_action_model("action")   # 🔑 now uses GPT or Mistral depending on USE_GPT
    current_state_summary = _format_current_state(session_state)
    msg = _action_prompt.format_messages(
        query=user_query,
        current_state=current_state_summary
    )
    raw_output = action_model.invoke(msg).content.strip()

    try:
        new_data = json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            new_data = json.loads(cleaned)
        except Exception:
            new_data = {}

    # --- Patch: Robust protocol extraction ---
    # List of known protocols (expand as needed)
    KNOWN_PROTOCOLS = ["aave", "uniswap", "compound", "curve", "balancer", "sushiswap", "maker", "yearn", "1inch", "venus", "pancakeswap", "anchor"]
    import re
    # Search for protocol mentions in user_query
    found_protocol = None
    for proto in KNOWN_PROTOCOLS:
        pattern = re.compile(rf"\\b{proto}\\b", re.IGNORECASE)
        if pattern.search(user_query):
            found_protocol = proto.upper() if proto != "1inch" else "1inch"
            break

    # If protocol not set by LLM, set it from found_protocol
    if (not new_data.get("protocol")) and found_protocol:
        new_data["protocol"] = found_protocol

    # Step 3: Validate & map
    try:
        if "action" in new_data and new_data["action"]:
            try:
                new_data["action"] = DeFiAction(new_data["action"].lower())
            except ValueError:
                new_data["action"] = None
        new_result = ActionExtractionResult(**new_data)
    except ValueError:
        new_result = _get_default_action_state()

    # Step 4: Merge with session state
    final_result = _merge_action_results(session_state, new_result)

    # Step 5: Save back to Redis with TTL
    set_cached_response(cache_key, json.dumps(final_result.dict()), ttl=SESSION_TTL)

    return final_result


def extract_action_details_dict(user_query: str, user_id: str) -> Dict[str, Any]:
    """Backward compatibility wrapper that returns dict instead of schema."""
    result = extract_action_details(user_query, user_id)
    result_dict = result.dict()
    
    if result_dict.get("action"):
        result_dict["action"] = result_dict["action"].value
    
    return result_dict
