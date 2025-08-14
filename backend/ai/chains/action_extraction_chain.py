import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from backend.utils.cache import get_cached_response, set_cached_response

_action_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

_action_prompt = ChatPromptTemplate.from_template(
    """Extract structured DeFi action details from the user's request.
Return STRICT JSON only (no prose) with keys:
- action: one of ["deposit","withdraw","swap","stake","borrow","lend","provide_liquidity","repay","claim_rewards"]
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

DEFAULT_ACTION_STATE = {
    "action": None, "amount": None, "asset": None, "protocol": None, "chain": None,
    "apy_min": None, "apy_max": None, "slippage": None, "notes": None,
    "recipient": None, "duration": None
}

SESSION_TTL = 300  # 5 minutes


def extract_action_details(user_query: str, user_id: str) -> Dict[str, Any]:
    """
    Extract DeFi action details and merge with existing session state in Redis.
    """
    # Step 1: Load existing session state (if any)
    cache_key = f"action_session:{user_id}"
    cached_state_json = get_cached_response(cache_key)
    if cached_state_json:
        try:
            session_state = json.loads(cached_state_json)
        except json.JSONDecodeError:
            session_state = DEFAULT_ACTION_STATE.copy()
    else:
        session_state = DEFAULT_ACTION_STATE.copy()

    # Step 2: Extract new details
    msg = _action_prompt.format_messages(query=user_query)
    raw_output = _action_llm.invoke(msg).content.strip()

    try:
        new_data = json.loads(raw_output)
    except json.JSONDecodeError:
        cleaned = raw_output.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            new_data = json.loads(cleaned)
        except Exception:
            new_data = {}

    # Step 3: Merge new data into session state (only overwrite if new value not None)
    for key, default_val in DEFAULT_ACTION_STATE.items():
        if key in new_data and new_data[key] is not None:
            session_state[key] = new_data[key]

    # Step 4: Save updated session state back to Redis with TTL
    set_cached_response(cache_key, json.dumps(session_state), ttl=SESSION_TTL)

    return session_state
