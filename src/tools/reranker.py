"""
Cohere Rerank tool via Azure AI Foundry
"""
from typing import List
import requests
from langchain_core.documents import Document

from src.utils.config import settings
from src.utils.logger import logger
from src.utils.exceptions import RAGError


class CohereReranker:
    """Cohere Rerank v4.0 Fast via Azure AI Foundry HTTP API."""
    
    def __init__(self, deployment: str | None = None):
        """Initialize Cohere Reranker."""
        if not settings.azure_openai_api_key:
            raise RAGError("AZURE_OPENAI_API_KEY not set in .env")
        
        self.deployment = deployment or settings.cohere_rerank_deployment
        
        self.endpoint = settings.azure_openai_endpoint.rstrip("/")
        if not self.endpoint.endswith("/models"):
            base = self.endpoint.split("/api/")[0]
            self.endpoint = f"{base}/models"
        
        self.api_key = settings.azure_openai_api_key
        
        logger.info(f"Cohere Reranker initialized: {self.deployment}")
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: int = 5,
    ) -> List[Document]:
        """Rerank documents by relevance to query."""
        if not documents:
            return documents
        
        if not query or not query.strip():
            raise RAGError("Query cannot be empty")
        
        top_n = min(top_n, len(documents))
        
        try:
            url = f"{self.endpoint}/v1/rerank"
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key,
                "Authorization": f"Bearer {self.api_key}",
            }
            payload = {
                "model": self.deployment,
                "query": query,
                "documents": [doc.page_content for doc in documents],
                "top_n": top_n,
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Rerank API error: {response.status_code} - {response.text[:300]}")
                return self._try_fallback(query, documents, top_n)
            
            data = response.json()
            results = data.get("results", [])
            
            reranked = []
            for result in results:
                idx = result.get("index", -1)
                if 0 <= idx < len(documents):
                    reranked.append(documents[idx])
            
            if not reranked:
                return documents[:top_n]
            
            return reranked
            
        except Exception as e:
            logger.error(f"Rerank failed: {e}")
            return documents[:top_n]
    
    def _try_fallback(self, query: str, documents: List[Document], top_n: int):
        """Try fallback configuration for reranking."""
        return documents[:top_n]
