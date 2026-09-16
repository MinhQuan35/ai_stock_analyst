"""
LLM Factory re-export for backward compatibility.
"""
from src.models import get_chat_model, get_embeddings_model

__all__ = ["get_chat_model", "get_embeddings_model"]
