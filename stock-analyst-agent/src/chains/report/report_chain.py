"""
Report Generation Chain
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.llm import get_chat_model


class ReportChain:
    """Generate formatted reports."""
    
    REPORT_TEMPLATE = """Create a professional stock analysis report.

Data:
{data}

Format:
# Stock Analysis Report
## Executive Summary
[2-3 sentence overview]
## Key Metrics
[List of metrics]
## Analysis
[Detailed analysis]
## Recommendation
[BUY/HOLD/SELL with confidence]
## Disclaimer
"This is analysis only, not investment advice"
"""
    
    def __init__(self):
        self.llm = get_chat_model()
        self.prompt = ChatPromptTemplate.from_template(self.REPORT_TEMPLATE)
        self._chain = self.prompt | self.llm | StrOutputParser()
    
    async def ainvoke(self, data: str) -> str:
        return await self._chain.ainvoke({"data": data})
    
    def invoke(self, data: str) -> str:
        return self._chain.invoke({"data": data})
