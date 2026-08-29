"""
Agent Orchestrator - Coordinates multiple agents
"""
from src.agents.specialized.triage_agent import TriageAgent
from src.agents.specialized.analyst_agent import AnalystAgent
from src.agents.specialized.research_agent import ResearchAgent
from src.agents.specialized.reporter_agent import ReporterAgent


class AgentOrchestrator:
    """Coordinates multiple agents to handle complex queries."""
    
    def __init__(self):
        self.triage = TriageAgent()
        self.research = ResearchAgent()
        self.analyst = AnalystAgent()
        self.reporter = ReporterAgent()
    
    async def handle_query(self, query: str) -> dict:
        """Handle a user query by orchestrating multiple agents."""
        result = {
            "query": query,
            "triage": "",
            "research": "",
            "analysis": "",
            "report": "",
        }
        
        # Step 1: Triage
        triage_result = await self.triage.process(query)
        result["triage"] = triage_result.get("output", "")
        
        # Step 2: Research (if needed)
        research_result = await self.research.process(query)
        result["research"] = research_result.get("output", "")
        
        # Step 3: Analysis
        analysis_result = await self.analyst.process(query)
        result["analysis"] = analysis_result.get("output", "")
        
        # Step 4: Final Report
        if result["research"] or result["analysis"]:
            report = await self.reporter.create_report(
                result["research"],
                result["analysis"],
            )
            result["report"] = report
        
        return result
