"""
Base Agent class
"""
from abc import ABC, abstractmethod
from typing import Optional
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from src.constants import AgentRole
from src.exceptions import AgentError
from src.llm import get_chat_model


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        system_prompt: str,
        tools: list = None,
        model_name: str = None,
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.model_name = model_name
        self._agent = None
        self._llm = None
    
    def _initialize(self):
        """Initialize the agent."""
        if self._agent is None:
            self._llm = get_chat_model(model_name=self.model_name)
            self._agent = create_agent(
                model=self._llm,
                tools=self.tools,
                system_prompt=self.system_prompt,
            )
    
    @abstractmethod
    async def process(self, input: str, context: dict = None) -> str:
        """Process an input."""
        pass
    
    async def invoke(self, message: str, **kwargs) -> dict:
        """Invoke the agent."""
        try:
            self._initialize()
            result = self._agent.invoke({
                "messages": [HumanMessage(content=message)]
            })
            output = result.get("messages", [{}])[-1].content if result.get("messages") else ""
            return {"success": True, "output": output, "agent": self.name}
        except Exception as e:
            raise AgentError(f"Agent {self.name} failed: {str(e)}")
