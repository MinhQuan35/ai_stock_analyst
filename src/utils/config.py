"""
Configuration module - Azure AI Foundry + Qdrant
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Azure OpenAI (via Foundry)
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_chat_deployment: str = "gpt-4o"
    azure_embedding_deployment: str = "text-embedding-3-large"
    
    # Cohere Rerank (via Foundry)
    cohere_rerank_deployment: str = "Cohere-rerank-v4.0-fast"
    cohere_rerank_model: str = "Cohere-rerank-v4.0-fast"
    
    # Qdrant Vector DB
    qdrant_url: str = ""  # e.g., https://xxx.qdrant.io
    qdrant_api_key: str = ""
    qdrant_collection: str = "stock_knowledge"
    qdrant_vector_size: int = 3072  # text-embedding-3-large
    
    # Application
    app_name: str = "rag-stock-analyst"
    app_env: str = "development"
    app_debug: bool = True
    app_log_level: str = "INFO"
    
    # RAG
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50
    rag_top_k: int = 20
    rag_top_n: int = 5
    rag_data_dir: str = "./data/raw"
    rag_use_reranker: bool = True
    rag_vector_backend: str = "qdrant"  # "qdrant" or "faiss"
    
    # LLM
    llm_temperature: float = 0
    llm_max_tokens: int = 2000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()


# Singleton
settings = get_settings()
