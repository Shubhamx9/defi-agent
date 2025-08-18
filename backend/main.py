import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from backend.routes import query, health

# Load environment variables
load_dotenv()

from backend.config.settings import langchain_settings, security_settings
from backend.exception_handler import global_exception_handler
from backend.logging_setup import setup_logger
from backend.middleware.langsmith_tracer import LangSmithTracerMiddleware
from backend.models.schemas import HealthResponse
from backend.middleware.logging_middleware import log_requests


# Logger setup
logger = setup_logger()

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

# Enable LangSmith tracing
os.environ["LANGSMITH_API_KEY"] = langchain_settings.LANGSMITH_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "DeFi AI Assistant"

# Initialize FastAPI
app = FastAPI(
    title="DeFi AI Assistant",
    description="Cost-efficient DeFi AI Assistant with LangChain + LangSmith + Pinecone",
    version="1.0.0",
    docs_url="/docs" if security_settings.DEBUG else None,
    redoc_url="/redoc" if security_settings.DEBUG else None
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(log_requests)
app.add_middleware(LangSmithTracerMiddleware)

# Routes
app.include_router(query.router, prefix="/query")
app.include_router(health.router)

# Global error handler
app.add_exception_handler(Exception, global_exception_handler)

# Root endpoint
@app.get("/", response_model=HealthResponse)
@limiter.limit(f"{security_settings.RATE_LIMIT_PER_MINUTE}/minute")
def root(request: Request):
    logger.info("Root endpoint called")
    return HealthResponse(message="DeFi AI backend running")
