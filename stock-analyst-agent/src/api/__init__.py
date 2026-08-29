"""
API module
"""
from src.api.v1.routes.chat import router as chat_router
from src.api.v1.routes.agents import router as agents_router
from src.api.v1.routes.rag import router as rag_router
from src.api.v1.routes.metrics import router as metrics_router

__all__ = [
    "chat_router",
    "agents_router",
    "rag_router",
    "metrics_router",
]
