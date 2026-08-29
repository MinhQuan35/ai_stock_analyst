"""
Configuration module
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class AzureSettings(BaseSettings):
    """Azure OpenAI configuration."""
    api_key: str = Field(default="")
    endpoint: str = "https://hquan8696-5179-resource.services.ai.azure.com"
    api_version: str = "2024-10-21"
    chat_deployment: str = "gpt-4o"
    embedding_deployment: str = "text-embedding-3-large"
    
    class Config:
        env_prefix = "AZURE_"
        env_file = ".env"
        extra = "ignore"


class AppSettings(BaseSettings):
    """Application configuration."""
    app_name: str = "Stock Analyst Agent"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    max_iterations: int = 10
    request_timeout: int = 60
    
    class Config:
        env_prefix = "APP_"
        env_file = ".env"
        extra = "ignore"


class VectorStoreSettings(BaseSettings):
    """Vector store configuration."""
    store_type: str = "faiss"
    embedding_model: str = "text-embedding-3-large"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    persist_directory: str = "./data/embeddings"
    
    class Config:
        env_prefix = "VECTOR_"
        env_file = ".env"
        extra = "ignore"


class MemorySettings(BaseSettings):
    """Memory configuration."""
    memory_type: str = "buffer_window"
    max_token_limit: int = 2000
    return_messages: bool = True
    k: int = 10
    
    class Config:
        env_prefix = "MEMORY_"
        env_file = ".env"
        extra = "ignore"


class APISettings(BaseSettings):
    """API configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = ["*"]
    
    class Config:
        env_prefix = "API_"
        env_file = ".env"
        extra = "ignore"


# Load .env from project root
load_dotenv_path = Path(__file__).parent.parent.parent / ".env"
if load_dotenv_path.exists():
    from dotenv import load_dotenv
    load_dotenv(load_dotenv_path)


# Singleton instances
azure_settings = AzureSettings()
app_settings = AppSettings()
vector_settings = VectorStoreSettings()
memory_settings = MemorySettings()
api_settings = APISettings()
