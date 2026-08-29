"""
Triage Agent - Routes queries to appropriate agent
"""
from src.agents.base.base_agent import BaseAgent
from src.constants import AgentRole
from src.tools import FINANCIAL_TOOLS, MARKET_DATA_TOOLS


class TriageAgent(BaseAgent):
    """Agent that routes queries to the right specialist."""
    
    def __init__(self):
        system_prompt = """You are a Triage Agent for stock analysis.
        
Your job is to:
1. Understand the user's query
2. Determine if it's about: fundamental analysis, technical analysis, market data, portfolio, or general info
3. Provide a clear categorization

Reply with:
- Category: [fundamental/technical/market/portfolio/general]
- Priority: [high/medium/low]
- Brief summary of the request"""
        
        super().__init__(
            name="TriageAgent",
            role=AgentRole.TRIAGE,
            system_prompt=system_prompt,
            tools=[],
        )
    
    async def process(self, input: str, context: dict = None) -> str:
        return await self.invoke(input)
