"""
RAG Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from src.chains.rag.rag_chain import RAGChain
from src.vector_store import SimilarityRetriever, FAISSVectorStore, DirectoryDocumentLoader, RecursiveTextSplitter
from src.llm import get_embeddings_model
import re


router = APIRouter(prefix="/rag", tags=["rag"])


class RAGEvalRequest(BaseModel):
    query: str
    answer: str
    context: str
    retrieved_docs: list[str]
    relevant_docs: list[str]
    ground_truth: Optional[str] = None
    k: int = 5


@router.post("/evaluate")
async def evaluate_rag(request: RAGEvalRequest):
    """Evaluate RAG query."""
    retrieved = set(request.retrieved_docs[:request.k])
    relevant = set(request.relevant_docs)
    
    # Retrieval metrics
    precision = len(retrieved & relevant) / len(retrieved) if retrieved else 0
    recall = len(retrieved & relevant) / len(relevant) if relevant else 0
    mrr = 0.0
    for i, doc in enumerate(request.retrieved_docs[:request.k]):
        if doc in relevant:
            mrr = 1.0 / (i + 1)
            break
    
    # Generation metrics
    def tokenize(text):
        return set(re.findall(r'\b\w+\b', text.lower()))
    
    answer_words = tokenize(request.answer)
    context_words = tokenize(request.context)
    query_words = tokenize(request.query)
    
    faithfulness = len(answer_words & context_words) / len(answer_words) if answer_words else 0
    relevancy = len(query_words & answer_words) / len(query_words) if query_words else 0
    
    correctness = 0.0
    if request.ground_truth:
        truth_words = tokenize(request.ground_truth)
        correctness = len(answer_words & truth_words) / len(truth_words) if truth_words else 0
    
    overall = (precision + recall + faithfulness + relevancy) / 4
    
    return {
        "retrieval": {
            "precision": precision,
            "recall": recall,
            "mrr": mrr,
        },
        "generation": {
            "faithfulness": faithfulness,
            "relevancy": relevancy,
            "correctness": correctness,
            "hallucination": 1.0 - faithfulness,
        },
        "overall_score": overall,
    }


@router.post("/build")
async def build_index(directory: str = "./data/knowledge"):
    """Build FAISS index from knowledge base."""
    loader = DirectoryDocumentLoader(directory)
    docs = loader.load()
    
    splitter = RecursiveTextSplitter()
    chunks = splitter.split_documents(docs)
    
    embeddings = get_embeddings_model()
    store = FAISSVectorStore(embeddings)
    store.create_from_documents(chunks)
    store.save()
    
    return {
        "documents_loaded": len(docs),
        "chunks_created": len(chunks),
        "status": "success",
    }
