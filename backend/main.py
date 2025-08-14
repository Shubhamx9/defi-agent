import os
from fastapi import FastAPI
from dotenv import load_dotenv
from backend.routes import intent, query
from backend.config.settings import settings
from backend.middleware.error_handler import global_exception_handler
from backend.utils.logger import setup_logger
from backend.middleware.log_requests import log_requests
from backend.middleware.langsmith_tracer import LangSmithTracerMiddleware

# Load environment variables
load_dotenv()

# Logger setup
logger = setup_logger()

# Enable LangSmith tracing
os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "DeFi AI Assistant"

# Initialize FastAPI
app = FastAPI(
    title="DeFi AI Assistant",
    description="Hackathon project: LangChain + LangSmith + Pinecone",
    version="1.0.0"
)

# Middleware
app.middleware("http")(log_requests)
app.add_middleware(LangSmithTracerMiddleware)

# Routes
app.include_router(intent.router)
app.include_router(query.router, prefix="/query")

# Global error handler
app.add_exception_handler(Exception, global_exception_handler)

# Health check endpoint
@app.get("/")
def root():
    logger.info("Health check endpoint called")
    return {"status": "ok", "message": "DeFi AI backend running"}
