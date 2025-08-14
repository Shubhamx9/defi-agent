from starlette.middleware.base import BaseHTTPMiddleware
from langchain.callbacks.tracers.langchain import LangChainTracer
import os

class LangSmithTracerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.tracer = LangChainTracer(
            project_name=os.environ.get("LANGCHAIN_PROJECT", "DeFi AI Assistant")
        )

    async def dispatch(self, request, call_next):
        # Attach tracer to request.state for later use
        request.state.tracer = self.tracer
        response = await call_next(request)
        return response
