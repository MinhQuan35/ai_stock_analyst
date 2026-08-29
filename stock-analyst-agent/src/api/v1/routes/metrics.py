"""
Metrics Routes
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from src.monitoring.metrics.collector import MetricsCollector, get_collector
from src.constants import PRICING


router = APIRouter(prefix="/metrics", tags=["metrics"])


class TrackRequest(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    duration_ms: float
    satisfaction_score: Optional[float] = None
    error: Optional[str] = None


@router.post("/track")
async def track(request: TrackRequest):
    """Track metrics."""
    collector = get_collector()
    collector.record(
        model=request.model,
        input_tokens=request.input_tokens,
        output_tokens=request.output_tokens,
        duration_ms=request.duration_ms,
        satisfaction=request.satisfaction_score,
        error=request.error,
    )
    return {"message": "Tracked"}


@router.get("/")
async def get_metrics():
    """Get metrics summary."""
    return get_collector().get_summary()


@router.post("/reset")
async def reset():
    """Reset metrics."""
    global _collector
    _collector = MetricsCollector()
    return {"message": "Reset"}


@router.get("/pricing")
async def get_pricing():
    """Get model pricing."""
    return {"pricing": PRICING}
