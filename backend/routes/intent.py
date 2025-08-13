from fastapi import APIRouter, Body
from backend.ai.intent_classifier import get_intent_chain
from backend.ai.chains.intent_chain import get_qa_chain

router = APIRouter(prefix="/intent", tags=["Intent"])

@router.post("/")
async def handle_intent(user_query: str = Body(..., embed=True)):
    intent_chain = get_intent_chain()
    qa_chain = get_qa_chain()

    # Classify
    intent = intent_chain.run(query=user_query).strip()

    # Retrieve + Answer
    answer = qa_chain.run(user_query)

    return {
        "user_query": user_query,
        "intent": intent,
        "response": answer
    }
