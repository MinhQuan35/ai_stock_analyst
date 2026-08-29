"""
Reporter Agent - Creates final reports
"""
from src.agents.base.base_agent import BaseAgent
from src.constants import AgentRole


class ReporterAgent(BaseAgent):
    """Agent that creates final analysis reports."""
    
    def __init__(self):
        system_prompt = """You are a Reporter Agent.
        
Your job is to:
1. Combine inputs from research and analysis agents
2. Create comprehensive, well-structured reports
3. Format output professionally with clear sections
4. Always include:
   - Executive Summary
   - Key Metrics
   - Analysis
   - Recommendation
   - Disclaimer (This is analysis only, not investment advice)
"""
        
        super().__init__(
            name="ReporterAgent",
            role=AgentRole.REPORTER,
            system_prompt=system_prompt,
            tools=[],
        )
    
    async def process(self, input: str, context: dict = None) -> str:
        return await self.invoke(input)
    
    async def create_report(self, research_data: str, analysis: str) -> str:
        """Create a report from research and analysis."""
        prompt = f"""
Create a professional stock analysis report using the following information:

RESEARCH DATA:
{research_data}

ANALYSIS:
{analysis}

Format the report with:
1. Executive Summary
2. Current Status
3. Technical Analysis
4. Fundamental Analysis
5. Risk Assessment
6. Recommendation
7. Disclaimer
"""
        return (await self.invoke(prompt))["output"]
