"""
FAISS Vector Store Tool
"""
from pathlib import Path
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.utils.config import settings
from src.utils.logger import logger
from src.utils.exceptions import VectorStoreError


class FAISSStore:
    """FAISS-based vector store tool."""
    
    def __init__(self, embeddings: Embeddings, persist_dir: str | None = None):
        """Initialize FAISS store."""
        self.embeddings = embeddings
        self.persist_dir = Path(persist_dir or "./data/vector_store")
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._store: Optional[FAISS] = None
    
    def create_from_documents(self, documents: List[Document]) -> FAISS:
        """Create store from documents."""
        if not documents:
            raise VectorStoreError("No documents to index")
        
        logger.info(f"Creating FAISS index from {len(documents)} documents")
        
        try:
            self._store = FAISS.from_documents(documents, self.embeddings)
            logger.info("FAISS index created successfully")
            return self._store
        except Exception as e:
            raise VectorStoreError(f"Failed to create FAISS index: {str(e)}")
    
    def save(self, name: str = "index") -> Path:
        """Save index to disk."""
        if not self._store:
            raise VectorStoreError("No index to save")
        
        path = self.persist_dir / name
        self._store.save_local(str(path))
        logger.info(f"Index saved to: {path}")
        return path
    
    def load(self, name: str = "index") -> FAISS:
        """Load index from disk."""
        path = self.persist_dir / name
        
        if not path.exists():
            raise VectorStoreError(f"Index not found: {path}")
        
        logger.info(f"Loading index from: {path}")
        
        try:
            self._store = FAISS.load_local(
                str(path),
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("Index loaded successfully")
            return self._store
        except Exception as e:
            raise VectorStoreError(f"Failed to load index: {str(e)}")
    
    def get_store(self) -> FAISS:
        """Get current store."""
        if not self._store:
            raise VectorStoreError("Store not initialized")
        return self._store
    
    def exists(self, name: str = "index") -> bool:
        """Check if index exists."""
        return (self.persist_dir / name).exists()
