import os
from fastapi import FastAPI
from dotenv import load_dotenv
from backend.routes import intent
from backend.config.settings import settings
from backend.middleware.error_handler import global_exception_handler
from backend.utils.logger import setup_logger

# Load env vars
load_dotenv()

# Logger setup
logger = setup_logger()

# Enable LangSmith
os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "DeFi AI Assistant"

# Init FastAPI
app = FastAPI(
    title="DeFi AI Assistant",
    description="Hackathon project: LangChain + LangSmith + Pinecone",
    version="1.0.0"
)

# Routes
app.include_router(intent.router)

# Global error handler
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/")
def root():
    logger.info("Health check endpoint called")
    return {"status": "ok", "message": "DeFi AI backend running"}
