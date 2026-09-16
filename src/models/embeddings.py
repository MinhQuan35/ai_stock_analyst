"""
Embeddings Client - Azure OpenAI via Foundry (with rate-limit safe batching)
"""
from functools import lru_cache
from langchain_openai import AzureOpenAIEmbeddings

from src.utils.config import settings
from src.utils.logger import logger


@lru_cache()
def get_embeddings_model(deployment: str | None = None) -> AzureOpenAIEmbeddings:
    """Get Azure OpenAI embeddings model via Foundry."""
    if not settings.azure_openai_api_key:
        raise ValueError("AZURE_OPENAI_API_KEY not set in .env")
    
    model = AzureOpenAIEmbeddings(
        azure_deployment=deployment or settings.azure_embedding_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        chunk_size=100,  # Safe batching to prevent Azure OpenAI 429 RateLimit
    )
    logger.info(f"Embeddings model loaded: {deployment or settings.azure_embedding_deployment}")
    return model
