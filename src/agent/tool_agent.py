"""
Tool-Calling Agent for Global and Vietnam Stock Market Analysis.
Uses direct LLM Tool Binding (langchain_core) for high performance and universal compatibility.
"""
from typing import List, Optional
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool

from src.models import get_chat_model
from src.prompts import TOOL_AGENT_SYSTEM_PROMPT
from src.utils.logger import logger
from src.utils.exceptions import RAGError


class StockAnalystToolAgent:
    """Autonomous Financial Analyst Agent with native LLM Tool Calling."""

    def __init__(
        self,
        tools: List[BaseTool],
        system_prompt: Optional[str] = None,
        verbose: bool = True,
    ):
        """Initialize tool-calling agent with financial tools."""
        self.tools = tools
        self.tools_by_name = {t.name: t for t in tools}
        self.system_prompt = system_prompt or TOOL_AGENT_SYSTEM_PROMPT
        self.llm = get_chat_model()
        self.model_with_tools = self.llm.bind_tools(tools)
        self.verbose = verbose

    def query(self, question: str) -> str:
        """Process user inquiry synchronously via native tool calling."""
        if not question or not question.strip():
            raise RAGError("Question cannot be empty.")
        
        logger.info(f"Tool Agent processing query: {question[:60]}")
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=question.strip()),
            ]

            ai_msg = self.model_with_tools.invoke(messages)
            messages.append(ai_msg)

            # Check if LLM requested tool execution
            if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
                for tool_call in ai_msg.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call.get("id", "call_1")

                    selected_tool = self.tools_by_name.get(tool_name)
                    if selected_tool:
                        try:
                            logger.info(f"Executing tool '{tool_name}' with args {tool_args}")
                            tool_output = selected_tool.invoke(tool_args)
                        except Exception as e:
                            tool_output = f"Tool execution error: {str(e)}"
                    else:
                        tool_output = f"Tool '{tool_name}' not available."

                    messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_id))

                # Synthesize final answer based on tool outputs
                final_res = self.llm.invoke(messages)
                return getattr(final_res, "content", str(final_res))

            return getattr(ai_msg, "content", str(ai_msg))

        except Exception as e:
            logger.error(f"Tool Agent execution error: {e}")
            raise RAGError(f"Agent execution failed: {str(e)}")

    async def aquery(self, question: str) -> str:
        """Process user inquiry asynchronously."""
        return self.query(question)
