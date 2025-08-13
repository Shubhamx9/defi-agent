# Intent classification with LangChain LLM
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from backend.config.settings import settings

INTENT_PROMPT = """Classify the following DeFi-related query into one intent:
deposit, withdraw, balance_query, apy_query, protocol_info, general_defi

Query: {query}
Intent:"""

def get_intent_chain():
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY
    )
    prompt = PromptTemplate(template=INTENT_PROMPT, input_variables=["query"])
    return LLMChain(llm=llm, prompt=prompt)
