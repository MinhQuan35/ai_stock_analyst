"""
RAG Chain
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.llm import get_chat_model
from src.vector_store import SimilarityRetriever


class RAGChain:
    """Retrieval-Augmented Generation chain."""
    
    RAG_TEMPLATE = """You are a financial analyst assistant. Use the following context to answer the question.
If you don't know the answer, say so. Don't make up information.

Context:
{context}

Question: {question}

Answer:"""
    
    def __init__(self, retriever: SimilarityRetriever):
        self.retriever = retriever
        self.llm = get_chat_model()
        self.prompt = ChatPromptTemplate.from_template(self.RAG_TEMPLATE)
        self._chain = None
    
    def _format_docs(self, docs):
        """Format documents for prompt."""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def get_chain(self):
        """Get the RAG chain."""
        if self._chain is None:
            self._chain = (
                {
                    "context": self.retriever.retrieve | self._format_docs,
                    "question": RunnablePassthrough(),
                }
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
        return self._chain
    
    async def ainvoke(self, question: str) -> str:
        """Async invoke."""
        return await self.get_chain().ainvoke(question)
    
    def invoke(self, question: str) -> str:
        """Sync invoke."""
        return self.get_chain().invoke(question)
