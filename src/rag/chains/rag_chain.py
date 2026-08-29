"""
RAG Chain - Combines retrieval with LLM generation
"""
from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.llm import get_chat_model
from src.rag.retrievers.similarity_retriever import SimilarityRetriever
from src.utils import logger
from src.exceptions import RAGError


class RAGChain:
    """RAG chain using LCEL syntax."""
    
    DEFAULT_TEMPLATE = """You are a helpful assistant. Answer the question based ONLY on the following context.
If you don't know the answer, say "I don't know based on the available information."

Context:
{context}

Question: {question}

Answer:"""
    
    def __init__(self, retriever: SimilarityRetriever, template: str | None = None):
        """Initialize RAG chain."""
        self.retriever = retriever
        self.template = template or self.DEFAULT_TEMPLATE
        self.llm = get_chat_model()
        self._chain = None
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format documents into a single string."""
        if not docs:
            return "No relevant context found."
        return "\n\n---\n\n".join(doc.page_content for doc in docs)
    
    def _build_chain(self):
        """Build the LCEL chain."""
        prompt = ChatPromptTemplate.from_template(self.template)
        
        chain = (
            {
                "context": self.retriever.as_langchain_retriever() | self._format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain
    
    def get_chain(self):
        """Get the chain (lazy init)."""
        if not self._chain:
            self._chain = self._build_chain()
        return self._chain
    
    def query(self, question: str) -> str:
        """Ask a question and get an answer."""
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
