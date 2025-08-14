from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()
from backend.config.settings import settings

# Connect to Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX)

def query_vector_db(embedding: list[float], top_k: int = 5):
    response = index.query(
        vector=embedding,
        top_k=top_k,
        include_metadata=True,
        include_values=False
    )
    return response.matches
