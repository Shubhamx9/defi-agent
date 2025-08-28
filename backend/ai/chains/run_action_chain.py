"""
DeFi Action Engine built on Coinbase AgentKit.
Handles transfers, balances, x402 payments, price queries, and APY lookups.
"""

from backend.logging_setup import logger
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable
from backend.utils.model_selector import tiny_model
from backend.ai.extractors.transfer_extractor import extract_transfer_parameters
from backend.ai.extractors.price_extractor import extract_price_parameters
from backend.ai.extractors.balance_extractor import extract_balance_parameters
from backend.utils.apy import get_top_low_yield_apy_pools
from backend.ai.extractors.x402_extractor import extract_x402_parameters


_action_sub_intent_prompt = ChatPromptTemplate.from_template(
    """Classify the user's request into one of the following actions:

- check_balance → user asks about wallet balance
- get_address → user asks for their wallet address
- send_tokens → user wants to transfer tokens
- pay_service → user wants to pay for an API/service (x402) (only classify here if API/service is explicitly mentioned)
- confirm_payment → user confirms a pending x402 payment
- get_price → user asks for a token price
- wrap_eth → user wants to wrap or unwrap ETH
- search_apy → user wants to search for best APY

User query: {query}

Respond with ONLY one label from the list above.
Label:"""
)


@traceable(name="DeFi Action Sub-Intent Classification")
def classify_action_sub_intent(query: str) -> str:
    try:
        model = tiny_model()
        msg = _action_sub_intent_prompt.format_messages(query=query.strip())
        out = model.invoke(msg)
        return out.content.strip().lower() if out and out.content else "check_balance"
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return "check_balance"


# ---------- MAIN ORCHESTRATOR ----------
@traceable(name="DeFi Action Execution")
async def run_action_chain(query: str, user_id: str) -> str:

    # Lazy import to avoid circular deps
    from backend.ai.actions.cdp_actions import (
        get_wallet_balance_cdp,
        get_wallet_address_cdp,
        send_tokens_cdp,
        process_x402_request,
        get_token_price,
    )
    from backend.utils.apy import get_top_low_yield_apy_pools

    msg = _action_sub_intent_prompt.format_messages(query=query.strip())
    intent = classify_action_sub_intent(query)

    if intent == "check_balance":
        return await get_wallet_balance_cdp(user_id)

    elif intent == "get_address":
        return await get_wallet_address_cdp(user_id)

    elif intent == "send_tokens":
        try:
            params = extract_transfer_parameters(query)
            return await send_tokens_cdp(user_id, params)
        except Exception as e:
            logger.error(f"Transfer extraction failed: {e}")
            return "❌ Could not process transfer request."

    elif intent in ["pay_service", "confirm_payment"]:
        return await process_x402_request(query, user_id)

    elif intent == "get_price":
        try:
            params = extract_price_parameters(query)
            price = await get_token_price(params["symbol"])
            return f"💲 Current price of {params['symbol'].upper()}: ${price:.4f}"
        except Exception as e:
            logger.error(f"Price extraction failed: {e}")
            return "❌ Could not fetch token price."

    elif intent == "wrap_eth":
        return "⚠️ Wrapping/unwrapping ETH Will be available SOON."

    elif intent == "search_apy":
        try:
            params = extract_balance_parameters(query)
            pools = get_top_low_yield_apy_pools(params.get("top", 3), highest=True)
            if not pools:
                return "❌ No high APY pools found."
            response = "🏆 Top APY Pools:\n" + "\n".join(
                [f"- {p['name']}: {p['apy']}% ({p['link']})" for p in pools]
            )
            return response
        except Exception as e:
            logger.error(f"APY search failed: {e}")
            return "❌ Could not search for APY pools."

    else:
        return "❌ Unrecognized action intent."
