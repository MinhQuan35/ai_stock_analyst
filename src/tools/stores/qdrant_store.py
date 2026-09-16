"""
Qdrant Vector Store Tool
"""
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models

from src.utils.config import settings
from src.utils.logger import logger
from src.utils.exceptions import VectorStoreError


class QdrantStore:
    """Qdrant-based vector store (Cloud or Local)."""
    
    def __init__(
        self,
        embeddings: Embeddings,
        collection_name: str | None = None,
        url: str | None = None,
        api_key: str | None = None,
        prefer_grpc: bool = False,
    ):
        """Initialize Qdrant store."""
        self.embeddings = embeddings
        self.collection_name = collection_name or settings.qdrant_collection
        self.url = url or settings.qdrant_url
        self.api_key = api_key or settings.qdrant_api_key
        
        if not self.url:
            raise VectorStoreError(
                "QDRANT_URL not set. Get a free cluster at https://cloud.qdrant.io"
            )
        
        if not self.api_key:
            raise VectorStoreError(
                "QDRANT_API_KEY not set. Get it from your Qdrant Cloud dashboard"
            )
        
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
            prefer_grpc=prefer_grpc,
        )
        
        self._store: Optional[QdrantVectorStore] = None
        
        logger.info(f"Qdrant client connected: {self.url[:50]}...")
        logger.info(f"Collection: {self.collection_name}")
    
    def create_from_documents(self, documents: List[Document]) -> QdrantVectorStore:
        """Create collection and add documents."""
        if not documents:
            raise VectorStoreError("No documents to index")
        
        logger.info(f"Creating Qdrant collection with {len(documents)} docs")
        
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted existing collection: {self.collection_name}")
        except Exception:
            pass
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=settings.qdrant_vector_size,
                distance=models.Distance.COSINE,
            ),
        )
        
        self._store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
        
        self._store.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to Qdrant")
        return self._store
    
    def load(self) -> QdrantVectorStore:
        """Load existing collection."""
        if not self.client.collection_exists(self.collection_name):
            raise VectorStoreError(f"Collection {self.collection_name} does not exist")
        
        self._store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
        )
        logger.info(f"Loaded existing collection: {self.collection_name}")
        return self._store
    
    def get_store(self) -> QdrantVectorStore:
        """Get the current store."""
        if not self._store:
            raise VectorStoreError("Store not initialized.")
        return self._store
    
    def exists(self) -> bool:
        """Check if collection exists."""
        return self.client.collection_exists(self.collection_name)
    
    def count(self) -> int:
        """Get number of points in collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception:
            return 0
    
    def search_with_filter(
        self,
        query: str,
        k: int = 5,
        source_filter: str | None = None,
    ) -> List[Document]:
        """Search with optional metadata filter."""
        if not self._store:
            raise VectorStoreError("Store not initialized")
        
        if source_filter:
            results = self._store.similarity_search(
                query,
                k=k,
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.source",
                            match=models.MatchValue(value=source_filter),
                        )
                    ]
                ),
            )
        else:
            results = self._store.similarity_search(query, k=k)
        
        return results
