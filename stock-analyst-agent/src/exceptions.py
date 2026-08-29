"""
Custom exceptions
"""


class StockAnalystError(Exception):
    """Base exception."""
    pass


class AgentError(StockAnalystError):
    """Agent execution error."""
    pass


class ToolExecutionError(StockAnalystError):
    """Tool execution error."""
    pass


class RAGError(StockAnalystError):
    """RAG pipeline error."""
    pass


class MemoryError(StockAnalystError):
    """Memory operation error."""
    pass


class ConfigurationError(StockAnalystError):
    """Configuration error."""
    pass


class APIError(StockAnalystError):
    """API error."""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded."""
    pass


class ValidationError(StockAnalystError):
    """Validation error."""
    pass


class VectorStoreError(StockAnalystError):
    """Vector store error."""
    pass
