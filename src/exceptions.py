"""
Custom exceptions re-export for backward compatibility.
"""
from src.utils.exceptions import (
    AppError,
    ConfigError,
    DocumentLoadError,
    ChunkingError,
    EmbeddingError,
    VectorStoreError,
    RetrievalError,
    LLMError,
    RAGError,
)

__all__ = [
    "AppError",
    "ConfigError",
    "DocumentLoadError",
    "ChunkingError",
    "EmbeddingError",
    "VectorStoreError",
    "RetrievalError",
    "LLMError",
    "RAGError",
]
