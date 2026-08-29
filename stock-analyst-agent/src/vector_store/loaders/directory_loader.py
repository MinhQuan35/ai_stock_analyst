"""
Directory Document Loader
"""
from pathlib import Path
from typing import Optional
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document


class DirectoryDocumentLoader:
    """Load documents from directory."""
    
    def __init__(self, directory: str, glob_pattern: str = "**/*.md"):
        self.directory = Path(directory)
        self.glob_pattern = glob_pattern
    
    def load(self) -> list[Document]:
        """Load all matching documents."""
        if not self.directory.exists():
            return []
        
        loader = DirectoryLoader(
            str(self.directory),
            glob=self.glob_pattern,
            loader_cls=TextLoader,
        )
        return loader.load()
    
    def load_with_metadata(self) -> list[dict]:
        """Load with metadata."""
        docs = self.load()
        return [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", ""),
                "metadata": doc.metadata,
            }
            for doc in docs
        ]
