"""
Research Agent - Gathers information
"""
from src.agents.base.base_agent import BaseAgent
from src.constants import AgentRole
from src.tools import MARKET_DATA_TOOLS


class ResearchAgent(BaseAgent):
    """Agent that gathers market data and news."""
    
    def __init__(self):
        system_prompt = """You are a Research Agent.
        
Your job is to:
1. Find current stock quotes and market data
2. Get company information
3. Retrieve historical prices
4. Search for relevant news

Use the tools available to gather accurate, up-to-date information.
Be precise with numbers and always cite the source."""
        
        super().__init__(
            name="ResearchAgent",
            role=AgentRole.RESEARCHER,
            system_prompt=system_prompt,
            tools=MARKET_DATA_TOOLS,
        )
    
    async def process(self, input: str, context: dict = None) -> str:
        return await self.invoke(input)
