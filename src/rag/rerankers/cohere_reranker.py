"""
Cohere Rerank v4.0 Fast via Azure AI Foundry (HTTP API)
"""
from typing import List
import requests
from langchain_core.documents import Document

from src.config import settings
from src.utils import logger
from src.exceptions import RAGError


class CohereReranker:
    """
    Cohere Rerank v4.0 Fast via Azure AI Foundry HTTP API.
    
    Usage:
        reranker = CohereReranker()
        reranked = reranker.rerank(query, documents, top_n=5)
    """
    
    def __init__(self, deployment: str | None = None):
        """Initialize Cohere Reranker."""
        if not settings.azure_openai_api_key:
            raise RAGError("AZURE_OPENAI_API_KEY not set in .env")
        
        self.deployment = deployment or settings.cohere_rerank_deployment
        
        # Build endpoint URL for Cohere Rerank
        # Format: https://<resource>.services.ai.azure.com/models
        self.endpoint = settings.azure_openai_endpoint.rstrip("/")
        if not self.endpoint.endswith("/models"):
            # Remove /api/projects/... if present
            base = self.endpoint.split("/api/")[0]
            self.endpoint = f"{base}/models"
        
        self.api_key = settings.azure_openai_api_key
        
        logger.info(f"Cohere Reranker initialized: {self.deployment}")
        logger.info(f"Endpoint: {self.endpoint}")
    
    def rerank(
        self,
        query: str,
        documents: List[Document],
        top_n: int = 5,
    ) -> List[Document]:
        """
        Rerank documents by relevance to query.
        
        Args:
            query: User query
            documents: List of documents to rerank
            top_n: Number of top results to return
            
        Returns:
            Reranked list of documents (most relevant first)
        """
        if not documents:
            return documents
        
        if not query or not query.strip():
            raise RAGError("Query cannot be empty")
        
        top_n = min(top_n, len(documents))
        
        try:
            # Prepare request
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
            
            logger.info(f"Calling Cohere Rerank: {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Rerank API error: {response.status_code} - {response.text[:300]}")
                # Try alternative endpoint format
                return self._try_fallback(query, documents, top_n)
            
            data = response.json()
            results = data.get("results", [])
            
            # Map results back to Document objects
            reranked = []
            for result in results:
                idx = result.get("index", -1)
                score = result.get("relevance_score", 0)
                if 0 <= idx < len(documents):
                    reranked.append(documents[idx])
                    logger.debug(f"  Doc {idx}: score={score:.3f}")
            
            if not reranked:
                logger.warning("No results from rerank, using original order")
                return documents[:top_n]
            
            scores = [r.get("relevance_score", 0) for r in results[:3]]
            logger.info(f"Reranked {len(documents)} → {len(reranked)} docs (top scores: {[round(s, 3) for s in scores]})")
            return reranked
            
        except Exception as e:
            logger.error(f"Rerank failed: {e}")
            logger.warning("Falling back to original order")
            return documents[:top_n]
    
    def _try_fallback(self, query: str, documents: List[Document], top_n: int):
        """Try alternative endpoint format."""
        try:
            # Try /api/projects/.../inference/rerank
            url = f"{self.endpoint}/v1/rerank"
            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key,
            }
            
            payload = {
                "model": self.deployment,
                "query": query,
                "documents": [doc.page_content for doc in documents],
                "top_n": top_n,
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                reranked = []
                for result in results:
                    idx = result.get("index", -1)
                    if 0 <= idx < len(documents):
                        reranked.append(documents[idx])
                return reranked if reranked else documents[:top_n]
        except Exception:
            pass
        
        return documents[:top_n]
