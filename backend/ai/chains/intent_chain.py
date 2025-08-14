from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable

# Allowed labels for validation
_ALLOWED_INTENTS = {"general_query", "action_request", "clarification"}

# Instantiate once (saves time & cost)
_intent_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

_intent_prompt = ChatPromptTemplate.from_template(
    """Classify the user's message into exactly one of:
- general_query  (informational/educational)
- action_request (user wants to perform a DeFi action like deposit/withdraw/swap/borrow/lend/stake)
- clarification  (ambiguous or missing details)

Reply with ONLY the label.

User: {query}"""
)

@traceable(name="DeFi Intent Classification")
def classify_intent(query: str) -> str:
    """Classify query into general_query, action_request, or clarification."""
    
    # Basic input sanitization
    if not query or not query.strip():
        return "clarification"  # default for empty input
    
    # Run the model
    msg = _intent_prompt.format_messages(query=query.strip())
    out = _intent_llm.invoke(msg)
    
    intent = out.content.strip().lower()
    
    # Validate output; fallback to clarification if invalid
    if intent not in _ALLOWED_INTENTS:
        intent = "clarification"
    
    return intent
