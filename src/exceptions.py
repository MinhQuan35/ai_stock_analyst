"""
Custom exceptions
"""


class AppError(Exception):
    """Base exception."""
    pass


class ConfigError(AppError):
    """Configuration error."""
    pass


class DocumentLoadError(AppError):
    """Document loading error."""
    pass


class ChunkingError(AppError):
    """Text chunking error."""
    pass


class EmbeddingError(AppError):
    """Embedding generation error."""
    pass


class VectorStoreError(AppError):
    """Vector store error."""
    pass


class RetrievalError(AppError):
    """Retrieval error."""
    pass


class LLMError(AppError):
    """LLM error."""
    pass


class RAGError(AppError):
    """RAG pipeline error."""
    pass
