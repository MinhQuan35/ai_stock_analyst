"""
Analysis Chain
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.llm import get_chat_model


class AnalysisChain:
    """Stock analysis chain."""
    
    ANALYSIS_TEMPLATE = """You are a stock analyst. Analyze the following stock data:

Stock: {symbol}
Price: {price}
EPS: {eps}
Dividend: {dividend}

Provide:
1. P/E ratio interpretation
2. Dividend yield analysis
3. Overall assessment
4. Recommendation (BUY/HOLD/SELL)
5. Disclaimer: "This is analysis only, not investment advice"
"""
    
    def __init__(self):
        self.llm = get_chat_model()
        self.prompt = ChatPromptTemplate.from_template(self.ANALYSIS_TEMPLATE)
        self._chain = self.prompt | self.llm | StrOutputParser()
    
    async def ainvoke(self, **kwargs) -> str:
        return await self._chain.ainvoke(kwargs)
    
    def invoke(self, **kwargs) -> str:
        return self._chain.invoke(kwargs)
