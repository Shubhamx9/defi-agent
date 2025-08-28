from pydantic_settings import BaseSettings
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

class LangChainSettings(BaseSettings):
    LANGSMITH_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "DeFi AI Assistant"

    class Config:
        env_file = ".env"


class OpenAISettings(BaseSettings):
    OPENAI_API_KEY: Optional[str] = None
    class Config:
        env_file = ".env"


class PineconeSettings(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_INDEX: str

    class Config:
        env_file = ".env"


class RedisSettings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = ""

    class Config:
        env_file = ".env"


class ModelSettings(BaseSettings):
    DEFAULT_MODEL: str = "gpt-5-mini"
    FALLBACK_MODEL: str = "gpt-5-mini"
    DEFAULT_TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 1000

    INTENT_MODEL: str = "gpt-5-nano"
    QUERY_MODEL: str = "gpt-5-mini"
    ACTION_MODEL: str = "gpt-5-mini"
    ADVANCED_MODEL: str = "gpt-5"

    class Config:
        env_file = ".env"


class SecuritySettings(BaseSettings):
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]

    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    class Config:
        env_file = ".env"


class VectorSettings(BaseSettings):
    VECTOR_SEARCH_TOP_K: int = 3
    HIGH_CONFIDENCE_THRESHOLD: float = 0.98
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.90

    class Config:
        env_file = ".env"


class SessionSettings(BaseSettings):
    SESSION_TTL: int = 300
    MAX_CONVERSATION_HISTORY: int = 10

    class Config:
        env_file = ".env"

class ChatBot(BaseSettings):
    USE_GPT: bool = False

    class Config:
        env_file = ".env"

class CDPSettings(BaseSettings):
    CDP_API_KEY_ID: str
    CDP_API_KEY_SECRET: str
    CDP_WALLET_SECRET: str
    CDP_NETWORK_ID: str = "base-sepolia"
    CDP_PAYMASTER_URL: str
    class Config:
        env_file = ".env"




# Instantiate
openai_settings = OpenAISettings()
pinecone_settings = PineconeSettings()
redis_settings = RedisSettings()
model_settings = ModelSettings()
security_settings = SecuritySettings()
vector_settings = VectorSettings()
session_settings = SessionSettings()
chatbot_settings = ChatBot()
langchain_settings = LangChainSettings()
cdp_settings = CDPSettings()