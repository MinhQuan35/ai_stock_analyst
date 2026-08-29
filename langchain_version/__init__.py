"""
LangChain Version - AI Stock Analyst
"""
from .agent import chat, rag_chat, create_agent
from .tools import TOOLS
from .metrics import LangChainMetrics
from .config import (
    AZURE_API_KEY, AZURE_ENDPOINT, AZURE_API_VERSION,
    CHAT_DEPLOYMENT, EMBEDDING_DEPLOYMENT,
)

__all__ = [
    "chat",
    "rag_chat",
    "create_agent",
    "TOOLS",
    "LangChainMetrics",
    "AZURE_API_KEY",
    "AZURE_ENDPOINT",
]
