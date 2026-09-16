"""
FastAPI Request and Response schemas for AI Stock Analyst API
"""
from pydantic import BaseModel
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str
    use_reranker: bool = True


class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []


class IndexRequest(BaseModel):
    force_rebuild: bool = False


class EvalRequest(BaseModel):
    query: str
    answer: str
    context: str
    retrieved_docs: List[str]
    relevant_docs: List[str]
    ground_truth: Optional[str] = None
    expected_context: Optional[str] = None
    k: int = 5
