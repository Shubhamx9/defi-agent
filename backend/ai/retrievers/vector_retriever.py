# LangChain retriever for Pinecone vector store
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
from backend.config.settings import settings

def get_vector_retriever():
    # Init Pinecone
    pinecone.init(api_key=settings.PINECONE_API_KEY)

    # Embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

    # Existing index retriever
    vectorstore = Pinecone.from_existing_index(
        index_name=settings.PINECONE_INDEX,
        embedding=embeddings
    )

    return vectorstore.as_retriever(search_kwargs={"k": 3})
