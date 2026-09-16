"""
RAG Chain Executor - Combines retrieval + rerank + LLM generation
"""
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from src.models import get_chat_model
from src.tools.search import SimilarityRetriever
from src.tools.reranker import CohereReranker
from src.prompts import RAG_CONTEXT_TEMPLATE
from src.utils.logger import logger
from src.utils.exceptions import RAGError


class RAGChain:
    """RAG chain executor with optional reranker support."""
    
    DEFAULT_TEMPLATE = RAG_CONTEXT_TEMPLATE
    
    def __init__(
        self,
        retriever: SimilarityRetriever,
        reranker: Optional[CohereReranker] = None,
        top_n: int = 5,
        template: Optional[str] = None,
    ):
        """Initialize RAG chain."""
        self.retriever = retriever
        self.reranker = reranker
        self.top_n = top_n
        self.template = template or self.DEFAULT_TEMPLATE
        self.llm = get_chat_model()
        self._chain = None
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format documents into a single context string."""
        if not docs:
            return "No relevant context found."
        return "\n\n---\n\n".join(doc.page_content for doc in docs)
    
    def _retrieve_and_rerank(self, question: str) -> str:
        """Retrieve docs, optionally rerank, then format context."""
        documents = self.retriever.retrieve(question)
        
        if self.reranker and documents:
            documents = self.reranker.rerank(question, documents, top_n=self.top_n)
        else:
            documents = documents[:self.top_n]
        
        return self._format_docs(documents)
    
    def _build_chain(self):
        """Build the LCEL chain."""
        prompt = ChatPromptTemplate.from_template(self.template)
        
        chain = (
            {
                "context": RunnableLambda(self._retrieve_and_rerank),
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain
    
    def get_chain(self):
        """Get the LCEL chain."""
        if not self._chain:
            self._chain = self._build_chain()
        return self._chain
    
    def query(self, question: str) -> str:
        """Ask a question and generate answer."""
        if not question or not question.strip():
            raise RAGError("Question cannot be empty")
        
        logger.info(f"RAG query: {question[:50]}")
        
        try:
            answer = self.get_chain().invoke(question)
            logger.info(f"RAG answer generated ({len(answer)} chars)")
            return answer
        except Exception as e:
            raise RAGError(f"RAG query failed: {str(e)}")
    
    async def aquery(self, question: str) -> str:
        """Async query."""
        if not question or not question.strip():
            raise RAGError("Question cannot be empty")
        
        try:
            answer = await self.get_chain().ainvoke(question)
            return answer
        except Exception as e:
            raise RAGError(f"RAG async query failed: {str(e)}")
