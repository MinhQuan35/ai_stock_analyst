"""
Recursive Text Splitter
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class RecursiveTextSplitter:
    """Split text recursively."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    
    def split_text(self, text: str) -> list[str]:
        """Split text into chunks."""
        return self.splitter.split_text(text)
    
    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Split documents."""
        return self.splitter.split_documents(documents)
