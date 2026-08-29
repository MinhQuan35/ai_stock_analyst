"""
Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.constants import AnalysisType, Recommendation, Signal


class StockPrice(BaseModel):
    """Stock price data."""
    symbol: str
    price: float
    volume: int = 0
    timestamp: datetime = Field(default_factory=datetime.now)


class StockAnalysis(BaseModel):
    """Stock analysis result."""
    symbol: str
    name: str
    analysis_type: AnalysisType
    metrics: dict = {}
    recommendation: Recommendation = Recommendation.HOLD
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    signals: list[Signal] = []
    summary: str = ""
    disclaimer: str = "This is analysis only, not investment advice"
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatMessage(BaseModel):
    """Chat message."""
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    tool_calls: Optional[list[dict]] = None


class ChatRequest(BaseModel):
    """Chat request."""
    message: str
    session_id: str = "default"
    user_id: str = "anonymous"


class ChatResponse(BaseModel):
    """Chat response."""
    response: str
    session_id: str
    tool_calls: list[dict] = []
    metrics: dict = {}
    timestamp: datetime = Field(default_factory=datetime.now)


class RAGEvalRequest(BaseModel):
    """RAG evaluation request."""
    query: str
    answer: str
    context: str
    retrieved_docs: list[str]
    relevant_docs: list[str]
    ground_truth: Optional[str] = None
    k: int = 5


class RAGEvalResponse(BaseModel):
    """RAG evaluation response."""
    retrieval: dict
    generation: dict
    context: dict
    overall_score: float


class MetricsRecord(BaseModel):
    """Metrics record."""
    model: str
    input_tokens: int
    output_tokens: int
    duration_ms: float
    cost_usd: float = 0.0
    satisfaction_score: Optional[float] = None
    error: Optional[str] = None
