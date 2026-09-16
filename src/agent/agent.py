"""
Core Agent - End-to-end RAG Agent / RAGPipeline
"""
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document

from src.utils.config import settings
from src.utils.logger import logger
from src.utils.exceptions import RAGError, DocumentLoadError, ChunkingError
from src.models import get_embeddings_model
from src.tools.loaders import MultiFormatLoader, DirectoryLoader
from src.tools.splitter import RecursiveTextSplitter
from src.tools.stores.faiss_store import FAISSStore
from src.tools.search import SimilarityRetriever, HybridRetriever
from src.tools.reranker import CohereReranker
from src.tools.market_tools import (
    get_global_stock_quote,
    get_ai_tech_sector_movers,
    get_vietnam_stock_quote,
    get_vietnam_market_movers,
    create_rag_search_tool,
)
from src.agent.executor import RAGChain
from src.agent.tool_agent import StockAnalystToolAgent


class RAGPipeline:
    """End-to-end Financial Agent pipeline with Market Data Tools & Hybrid Search RAG."""
    
    INDEX_NAME = "stock_knowledge"
    
    def __init__(self, data_dir: str | None = None, use_reranker: bool | None = None):
        """Initialize RAG pipeline agent."""
        self.data_dir = Path(data_dir or settings.rag_data_dir)
        self.use_reranker = use_reranker if use_reranker is not None else settings.rag_use_reranker
        
        self.embeddings = get_embeddings_model()
        self.store = FAISSStore(self.embeddings)
        self.retriever: HybridRetriever | SimilarityRetriever | None = None
        self.reranker: CohereReranker | None = None
        self.chain: RAGChain | None = None
        self.tool_agent: StockAnalystToolAgent | None = None
        self.chunks: List[Document] = []
    
    def index(self, force_rebuild: bool = False) -> None:
        """Build the vector store index, BM25 index, and Tool Calling agent."""
        if not force_rebuild and self.store.exists(self.INDEX_NAME):
            logger.info(f"Loading existing vector index: {self.INDEX_NAME}")
            self.store.load(self.INDEX_NAME)
        else:
            documents = self._load_documents()
            self.chunks = self._split_documents(documents)
            logger.info("Building new vector store index...")
            self.store.create_from_documents(self.chunks)
            self.store.save(self.INDEX_NAME)
        
        # Build Hybrid Retriever (BM25 + Vector Search + RRF)
        self.retriever = HybridRetriever(self.store, chunks=self.chunks, k=settings.rag_top_k)

        
        if self.use_reranker:
            try:
                self.reranker = CohereReranker()
                logger.info("Reranker enabled")
            except Exception as e:
                logger.warning(f"Reranker disabled: {e}")
                self.reranker = None
        
        self.chain = RAGChain(self.retriever, reranker=self.reranker, top_n=settings.rag_top_n)

        # Initialize Tool-Calling Agent with Market Tools + RAG Tool
        try:
            rag_tool = create_rag_search_tool(self.retriever, reranker=self.reranker, top_n=settings.rag_top_n)
            tools = [
                get_global_stock_quote,
                get_ai_tech_sector_movers,
                get_vietnam_stock_quote,
                get_vietnam_market_movers,
                rag_tool,
            ]
            self.tool_agent = StockAnalystToolAgent(tools=tools)
            logger.info("StockAnalystToolAgent initialized successfully with market tools and RAG search.")
        except Exception as e:
            logger.warning(f"Tool agent initialization deferred: {e}")
            self.tool_agent = None

        logger.info("Financial AI Agent pipeline ready")
    
    def query(self, question: str) -> str:
        """Ask a question to the agent using autonomous tool calling with RAG fallback."""
        if self.tool_agent:
            try:
                return self.tool_agent.query(question)
            except Exception as e:
                logger.warning(f"Tool agent failed, falling back to RAG chain: {e}")

        if not self.chain:
            raise RAGError("Pipeline not indexed. Call index() first.")
        return self.chain.query(question)
    
    async def aquery(self, question: str) -> str:
        """Async query to the agent using autonomous tool calling with RAG fallback."""
        if self.tool_agent:
            try:
                return await self.tool_agent.aquery(question)
            except Exception as e:
                logger.warning(f"Async tool agent failed, falling back to RAG chain: {e}")

        if not self.chain:
            raise RAGError("Pipeline not indexed. Call index() first.")
        return await self.chain.aquery(question)

    
    def retrieve(self, query: str) -> List[Document]:
        """Retrieve relevant documents."""
        if not self.retriever:
            raise RAGError("Pipeline not indexed. Call index() first.")
        return self.retriever.retrieve(query)
    
    def _load_documents(self) -> List[Document]:
        """Load documents from data directory."""
        loader = MultiFormatLoader(str(self.data_dir))
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
