"""
LLM Client - Azure OpenAI via Foundry
"""
from functools import lru_cache
from langchain_openai import AzureChatOpenAI

from src.utils.config import settings
from src.utils.logger import logger


@lru_cache()
def get_chat_model(temperature: float | None = None, deployment: str | None = None) -> AzureChatOpenAI:
    """Get Azure OpenAI chat model via Foundry."""
    if not settings.azure_openai_api_key:
        raise ValueError("AZURE_OPENAI_API_KEY not set in .env")
    
    model = AzureChatOpenAI(
        azure_deployment=deployment or settings.azure_chat_deployment,
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        temperature=temperature if temperature is not None else settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )
    logger.info(f"Chat model loaded: {deployment or settings.azure_chat_deployment}")
    return model
