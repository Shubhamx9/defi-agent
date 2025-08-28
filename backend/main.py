import os
import asyncio

# CRITICAL: Force standard asyncio policy before any imports
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Disable uvloop by removing it from sys.modules if present
import sys
if 'uvloop' in sys.modules:
    del sys.modules['uvloop']

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

from backend.middleware.langsmith_tracer import LangSmithTracerMiddleware
from backend.middleware.log_requests import log_requests
from backend.config.settings import langchain_settings, security_settings
from backend.routes import query

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


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DeFi AI Assistant"}

#Routes
app.include_router(query.router, prefix="/query")