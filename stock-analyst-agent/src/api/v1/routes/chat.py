"""
Chat Routes
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.agents.orchestrator.coordinator import AgentOrchestrator
from src.monitoring.metrics.collector import get_collector
from src.schemas import ChatRequest, ChatResponse
import time

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the orchestrator (multiple agents)."""
    start = time.time()
    
    orchestrator = AgentOrchestrator()
    result = await orchestrator.handle_query(request.message)
    
    duration = (time.time() - start) * 1000
    
    # Record metrics
    collector = get_collector()
    collector.record(
        model="gpt-4o",
        input_tokens=len(request.message) // 4,  # Approximate
        output_tokens=len(result.get("report", "")) // 4,
        duration_ms=duration,
    )
    
    return ChatResponse(
        response=result.get("report") or result.get("analysis") or result.get("research"),
        session_id=request.session_id,
        tool_calls=[],
        metrics={"duration_ms": duration},
    )


@router.post("/simple")
async def simple_chat(request: ChatRequest):
    """Simple chat with just the analyst agent."""
    from src.agents.specialized.analyst_agent import AnalystAgent
    
    start = time.time()
    agent = AnalystAgent()
    result = await agent.process(request.message)
    duration = (time.time() - start) * 1000
    
    return {
        "response": result.get("output", ""),
        "session_id": request.session_id,
        "duration_ms": duration,
    }
