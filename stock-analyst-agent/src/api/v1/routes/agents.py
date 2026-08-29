"""
Agents Routes - Direct access to individual agents
"""
from fastapi import APIRouter
from pydantic import BaseModel
from src.agents.specialized.triage_agent import TriageAgent
from src.agents.specialized.analyst_agent import AnalystAgent
from src.agents.specialized.research_agent import ResearchAgent
from src.agents.specialized.reporter_agent import ReporterAgent


router = APIRouter(prefix="/agents", tags=["agents"])


class AgentRequest(BaseModel):
    message: str
    agent_type: str = "analyst"  # triage/analyst/research/reporter


@router.post("/invoke")
async def invoke_agent(request: AgentRequest):
    """Invoke a specific agent."""
    agents = {
        "triage": TriageAgent(),
        "analyst": AnalystAgent(),
        "research": ResearchAgent(),
        "reporter": ReporterAgent(),
    }
    
    agent = agents.get(request.agent_type, AnalystAgent())
    result = await agent.process(request.message)
    
    return {
        "agent": request.agent_type,
        "response": result.get("output", ""),
    }


@router.get("/list")
async def list_agents():
    """List available agents."""
    return {
        "agents": [
            {"name": "TriageAgent", "role": "triage", "description": "Routes queries to appropriate agent"},
            {"name": "AnalystAgent", "role": "analyst", "description": "Performs stock analysis"},
            {"name": "ResearchAgent", "role": "research", "description": "Gathers market data"},
            {"name": "ReporterAgent", "role": "reporter", "description": "Creates final reports"},
        ]
    }
