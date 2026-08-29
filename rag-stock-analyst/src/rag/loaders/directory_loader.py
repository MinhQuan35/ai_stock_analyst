"""
Document loader
"""
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader as LCDirectoryLoader, TextLoader
from langchain_core.documents import Document

from src.utils import logger
from src.exceptions import DocumentLoadError


class DirectoryLoader:
    """Load documents from a directory."""
    
    SUPPORTED_EXTENSIONS = [".md", ".txt"]
    
    def __init__(self, directory: str, glob_pattern: str = "**/*"):
        """Initialize loader."""
        self.directory = Path(directory)
        self.glob_pattern = glob_pattern
    
    def load(self) -> List[Document]:
        """Load all supported documents from directory."""
        if not self.directory.exists():
            raise DocumentLoadError(f"Directory not found: {self.directory}")
        
        logger.info(f"Loading documents from: {self.directory}")
        
        loader = LCDirectoryLoader(
            path=str(self.directory),
            glob=self.glob_pattern,
            loader_cls=TextLoader,
            silent_errors=True,
        )
        
        documents = loader.load()
        
        filtered = [
            doc for doc in documents
            if any(doc.metadata.get("source", "").endswith(ext) for ext in self.SUPPORTED_EXTENSIONS)
        ]
        
        logger.info(f"Loaded {len(filtered)} documents")
        return filtered
