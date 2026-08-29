"""
FAISS Vector Store
"""
from pathlib import Path
from typing import Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class FAISSVectorStore:
    """FAISS-based vector store."""
    
    def __init__(self, embeddings, persist_directory: str = "./data/embeddings"):
        self.embeddings = embeddings
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self._store: Optional[FAISS] = None
    
    def create_from_documents(self, documents: list[Document]) -> FAISS:
        """Create store from documents."""
        self._store = FAISS.from_documents(documents, self.embeddings)
        return self._store
    
    def save(self, name: str = "index"):
        """Save to disk."""
        if self._store:
            self._store.save_local(str(self.persist_directory / name))
    
    def load(self, name: str = "index") -> FAISS:
        """Load from disk."""
        path = self.persist_directory / name
        if path.exists():
            self._store = FAISS.load_local(
                str(path),
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
        return self._store
    
    def get_store(self) -> Optional[FAISS]:
        """Get current store."""
        return self._store
    
    def similarity_search(self, query: str, k: int = 5) -> list[Document]:
        """Search similar documents."""
        if self._store:
            return self._store.similarity_search(query, k=k)
        return []
