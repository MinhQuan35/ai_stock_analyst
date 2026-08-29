"""
RAG Pipeline - End-to-end RAG with Reranker
"""
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document

from src.config import settings
from src.utils import logger
from src.exceptions import RAGError, DocumentLoadError, ChunkingError, EmbeddingError, VectorStoreError
from src.llm import get_embeddings_model
from src.rag.loaders.directory_loader import DirectoryLoader
from src.rag.splitters.recursive_splitter import RecursiveTextSplitter
from src.rag.stores.faiss_store import FAISSStore
from src.rag.retrievers.similarity_retriever import SimilarityRetriever
from src.rag.rerankers.cohere_reranker import CohereReranker
from src.rag.chains.rag_chain import RAGChain


class RAGPipeline:
    """End-to-end RAG pipeline with reranker support."""
    
    INDEX_NAME = "stock_knowledge"
    
    def __init__(self, data_dir: str | None = None, use_reranker: bool | None = None):
        """Initialize RAG pipeline."""
        self.data_dir = Path(data_dir or settings.rag_data_dir)
        self.use_reranker = use_reranker if use_reranker is not None else settings.rag_use_reranker
        
        self.embeddings = get_embeddings_model()
        self.store = FAISSStore(self.embeddings)
        self.retriever: SimilarityRetriever | None = None
        self.reranker: CohereReranker | None = None
        self.chain: RAGChain | None = None
    
    def index(self, force_rebuild: bool = False) -> None:
        """Build the index from documents."""
        if not force_rebuild and self.store.exists(self.INDEX_NAME):
            logger.info(f"Loading existing index: {self.INDEX_NAME}")
            self.store.load(self.INDEX_NAME)
        else:
            logger.info("Building new index...")
            
            documents = self._load_documents()
            chunks = self._split_documents(documents)
            self.store.create_from_documents(chunks)
            self.store.save(self.INDEX_NAME)
        
        self.retriever = SimilarityRetriever(self.store, k=settings.rag_top_k)
        
        if self.use_reranker:
            try:
                self.reranker = CohereReranker()
                logger.info("Reranker enabled")
            except Exception as e:
                logger.warning(f"Reranker disabled: {e}")
                self.reranker = None
        
        self.chain = RAGChain(self.retriever, reranker=self.reranker, top_n=settings.rag_top_n)
        logger.info("RAG pipeline ready")
    
    def query(self, question: str) -> str:
        """Ask a question."""
        if not self.chain:
            raise RAGError("Pipeline not indexed. Call index() first.")
        return self.chain.query(question)
    
    async def aquery(self, question: str) -> str:
        """Async query."""
        if not self.chain:
            raise RAGError("Pipeline not indexed. Call index() first.")
        return await self.chain.aquery(question)
    
    def retrieve(self, query: str) -> List[Document]:
        """Retrieve relevant documents (with reranking if enabled)."""
        if not self.retriever:
            raise RAGError("Pipeline not indexed. Call index() first.")
        return self.retriever.retrieve(query)
    
    def _load_documents(self) -> List[Document]:
        """Load documents from data directory."""
        loader = DirectoryLoader(str(self.data_dir))
        try:
            return loader.load()
        except DocumentLoadError as e:
            logger.error(f"Failed to load documents: {e}")
            raise RAGError(f"Document loading failed: {str(e)}")
    
    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        splitter = RecursiveTextSplitter()
        try:
            return splitter.split(documents)
        except ChunkingError as e:
            logger.error(f"Failed to split documents: {e}")
            raise RAGError(f"Document chunking failed: {str(e)}")
