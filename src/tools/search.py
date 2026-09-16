"""
Hybrid Search (BM25 + Vector Search + RRF) and Similarity Search Retriever Tools
"""
from typing import List, Dict, Optional
from collections import defaultdict
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import BM25Retriever

from src.utils.config import settings
from src.utils.logger import logger
from src.utils.exceptions import RetrievalError


class SimilarityRetriever:
    """Similarity-based dense vector retriever tool."""
    
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
        """Get as LangChain retriever."""
        return self._get_retriever()


class HybridRetriever:
    """
    Hybrid Search Retriever: Combines BM25 Keyword Search + Dense Vector Search
    Merged using Reciprocal Rank Fusion (RRF).
    """
    
    def __init__(self, store, chunks: List[Document], k: int | None = None):
        """
        Initialize Hybrid Retriever.
        
        Args:
            store: Vector store instance (FAISS/Qdrant)
            chunks: List of indexed document chunks for BM25
            k: Top K results to return
        """
        self.store = store
        self.chunks = chunks
        self.k = k or settings.rag_top_k
        
        self.vector_retriever = store.get_store().as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.k},
        )
        
        # Build in-memory BM25 sparse keyword retriever (Instant C/Python)
        if chunks:
            self.bm25_retriever = BM25Retriever.from_documents(chunks, k=self.k)
        else:
            self.bm25_retriever = None
        
        logger.info(f"HybridRetriever initialized (BM25 + Vector + RRF, k={self.k})")
    
    def _reciprocal_rank_fusion(
        self,
        doc_lists: List[List[Document]],
        c: int = 60,
    ) -> List[Document]:
        """
        Reciprocal Rank Fusion (RRF) algorithm.
        RRF_Score(d) = sum(1 / (c + rank_i(d)))
        """
        rrf_scores: Dict[str, float] = defaultdict(float)
        doc_map: Dict[str, Document] = {}
        
        for doc_list in doc_lists:
            for rank, doc in enumerate(doc_list):
                # Use page content + source as document key
                doc_key = doc.page_content[:150] + doc.metadata.get("source", "")
                doc_map[doc_key] = doc
                rrf_scores[doc_key] += 1.0 / (c + rank + 1)
        
        # Sort documents by RRF score descending
        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        return [doc_map[k] for k in sorted_keys[: self.k]]
    
    def retrieve(self, query: str) -> List[Document]:
        """Execute Hybrid Search (BM25 + Vector Search + RRF)."""
        if not query or not query.strip():
            raise RetrievalError("Query cannot be empty")
        
        logger.info(f"Hybrid Search (BM25 + Vector) retrieving for: {query[:50]}")
        
        try:
            # 1. Dense Vector Retrieval
            vector_docs = self.vector_retriever.invoke(query)
            
            # 2. Sparse BM25 Keyword Retrieval
            bm25_docs = []
            if self.bm25_retriever:
                bm25_docs = self.bm25_retriever.invoke(query)
            
            # 3. Merge results using Reciprocal Rank Fusion (RRF)
            hybrid_docs = self._reciprocal_rank_fusion([vector_docs, bm25_docs])
            
            logger.info(
                f"Hybrid Search merged Vector ({len(vector_docs)}) + BM25 ({len(bm25_docs)}) "
                f"-> {len(hybrid_docs)} docs via RRF"
            )
            return hybrid_docs
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            raise RetrievalError(f"Hybrid retrieval failed: {str(e)}")
