# backend/config/settings.py
from pydantic_settings import BaseSettings

from typing import List

class Settings(BaseSettings):
    # API Keys
    LANGSMITH_API_KEY: str
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "defi-queries"
    
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "nothing"
    
    # Security and CORS
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Model configuration
    DEFAULT_MODEL: str = "gpt-4o-mini"
    DEFAULT_TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 1000
    
    # Vector search configuration
    VECTOR_SEARCH_TOP_K: int = 3
    HIGH_CONFIDENCE_THRESHOLD: float = 0.98
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.90
    
    # Session configuration
    SESSION_TTL: int = 300  # 5 minutes
    MAX_CONVERSATION_HISTORY: int = 10

    class Config:
        env_file = ".env"

settings = Settings()
