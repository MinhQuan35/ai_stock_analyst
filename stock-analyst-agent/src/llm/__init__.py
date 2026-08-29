"""
LLM Factory - Centralized LLM creation
"""
from functools import lru_cache
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from src.config import azure_settings


@lru_cache()
def get_chat_model(temperature: float = 0, model_name: str = None) -> AzureChatOpenAI:
    """Get cached chat model."""
    return AzureChatOpenAI(
        azure_deployment=model_name or azure_settings.chat_deployment,
        azure_endpoint=azure_settings.endpoint,
        api_key=azure_settings.api_key,
        api_version=azure_settings.api_version,
        temperature=temperature,
    )


@lru_cache()
def get_embeddings_model() -> AzureOpenAIEmbeddings:
    """Get cached embeddings model."""
    return AzureOpenAIEmbeddings(
        azure_deployment=azure_settings.embedding_deployment,
        azure_endpoint=azure_settings.endpoint,
        api_key=azure_settings.api_key,
        api_version=azure_settings.api_version,
    )


def get_model_by_name(name: str, temperature: float = 0) -> AzureChatOpenAI:
    """Get specific model by name."""
    return AzureChatOpenAI(
        azure_deployment=name,
        azure_endpoint=azure_settings.endpoint,
        api_key=azure_settings.api_key,
        api_version=azure_settings.api_version,
        temperature=temperature,
    )
