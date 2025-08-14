import os
from pinecone import Pinecone
from backend.config.settings import settings

def get_pinecone_client():
    return Pinecone(api_key=settings.PINECONE_API_KEY)
