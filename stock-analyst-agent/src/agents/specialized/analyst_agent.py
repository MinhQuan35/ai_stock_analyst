"""
Analyst Agent - Performs stock analysis
"""
from src.agents.base.base_agent import BaseAgent
from src.constants import AgentRole
from src.tools import FINANCIAL_TOOLS


class AnalystAgent(BaseAgent):
    """Agent that performs stock analysis."""
    
    def __init__(self):
        system_prompt = """You are a Stock Analyst Agent.
        
Your job is to:
1. Analyze stocks using fundamental and technical metrics
2. Calculate P/E, P/B, Dividend Yield, RSI, SMA, etc.
3. Provide clear buy/hold/sell recommendations
4. Always include disclaimer: "This is analysis only, not investment advice"

Use the tools available to perform calculations.
Be concise and data-driven in your analysis."""
        
        super().__init__(
            name="AnalystAgent",
            role=AgentRole.ANALYST,
            system_prompt=system_prompt,
            tools=FINANCIAL_TOOLS,
        )
    
    async def process(self, input: str, context: dict = None) -> str:
        return await self.invoke(input)
