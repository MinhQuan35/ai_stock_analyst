"""
Similarity retriever
"""
from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from src.config import settings
from src.utils import logger
from src.exceptions import RetrievalError


class SimilarityRetriever:
    """Similarity-based retriever."""
    
    def __init__(self, store, k: int | None = None):
        """Initialize retriever."""
        self.store = store
        self.k = k or settings.rag_top_k
        self._retriever: BaseRetriever | None = None
    
    def _get_retriever(self) -> BaseRetriever:
        """Get LangChain retriever."""
        if not self._retriever:
            self._retriever = self.store.get_store().as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.k},
            )
        return self._retriever
    
    def retrieve(self, query: str) -> List[Document]:
        """Retrieve relevant documents."""
        if not query or not query.strip():
            raise RetrievalError("Query cannot be empty")
        
        logger.info(f"Retrieving top {self.k} documents for: {query[:50]}")
        
        try:
            documents = self._get_retriever().invoke(query)
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        except Exception as e:
            raise RetrievalError(f"Retrieval failed: {str(e)}")
    
    def as_langchain_retriever(self) -> BaseRetriever:
        """Get as LangChain retriever for chains."""
        return self._get_retriever()
