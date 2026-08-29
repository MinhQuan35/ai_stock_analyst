"""
Similarity Retriever
"""
from langchain_community.vectorstores import FAISS


class SimilarityRetriever:
    """Similarity-based retriever."""
    
    def __init__(self, vector_store: FAISS, k: int = 5):
        self.vector_store = vector_store
        self.k = k
    
    def retrieve(self, query: str) -> list:
        """Retrieve relevant documents."""
        return self.vector_store.similarity_search(query, k=self.k)
    
    def retrieve_with_score(self, query: str) -> list:
        """Retrieve with relevance scores."""
        return self.vector_store.similarity_search_with_score(query, k=self.k)
    
    def as_langchain_retriever(self):
        """Get as LangChain retriever."""
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.k},
        )
