# backend/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LANGSMITH_API_KEY: str
    # OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "defi-queries"

    class Config:
        env_file = ".env"

settings = Settings()
