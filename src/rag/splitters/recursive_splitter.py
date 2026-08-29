"""
Recursive text splitter
"""
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from src.config import settings
from src.utils import logger
from src.exceptions import ChunkingError


class RecursiveTextSplitter:
    """Split text into chunks recursively."""
    
    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        """Initialize splitter."""
        self.chunk_size = chunk_size or settings.rag_chunk_size
        self.chunk_overlap = chunk_overlap or settings.rag_chunk_overlap
        
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    
    def split(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        if not documents:
            raise ChunkingError("No documents to split")
        
        logger.info(f"Splitting {len(documents)} documents (size={self.chunk_size}, overlap={self.chunk_overlap})")
        
        chunks = self._splitter.split_documents(documents)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
