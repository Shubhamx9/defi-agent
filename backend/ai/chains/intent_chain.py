# LangChain chains for handling different intents
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from backend.ai.retrievers.vector_retriever import get_vector_retriever
from backend.config.settings import settings

def get_qa_chain():
    retriever = get_vector_retriever()
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openai_api_key=settings.OPENAI_API_KEY
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )
