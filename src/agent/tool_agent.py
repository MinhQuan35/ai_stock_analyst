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
        res = self.query_with_details(question)
        return res["answer"]

    def query_with_details(self, question: str) -> dict:
        """Process inquiry and return answer along with execution trajectory (tools called, outputs, success)."""
        if not question or not question.strip():
            raise RAGError("Question cannot be empty.")
            
        logger.info(f"Tool Agent processing query: {question[:60]}")
        tools_called = []
        tool_calls_detail = []
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=question.strip()),
            ]

            # Multi-round tool calling (bounded) so multi-hop comparisons can gather several sources
            max_rounds = 3
            final_res = None
            for _round in range(max_rounds):
                ai_msg = self.model_with_tools.invoke(messages)
                messages.append(ai_msg)

                if not getattr(ai_msg, "tool_calls", None):
                    final_res = ai_msg
                    break

                for tool_call in ai_msg.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call.get("id", "call_1")
                    tools_called.append(tool_name)

                    selected_tool = self.tools_by_name.get(tool_name)
                    success = True
                    if selected_tool:
                        try:
                            logger.info(f"Executing tool '{tool_name}' with args {tool_args}")
                            tool_output = selected_tool.invoke(tool_args)
                        except Exception as e:
                            tool_output = f"Tool execution error: {str(e)}"
                            success = False
                    else:
                        tool_output = f"Tool '{tool_name}' not available."
                        success = False

                    tool_calls_detail.append({
                        "tool": tool_name,
                        "args": tool_args,
                        "output": str(tool_output)[:500],
                        "success": success
                    })
                    messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_id))

            if final_res is None:
                # Tool budget exhausted: force a synthesis without further tool calls
                final_res = self.llm.invoke(messages)

            answer = getattr(final_res, "content", str(final_res))

            return {
                "answer": answer,
                "tools_called": tools_called,
                "tool_calls_detail": tool_calls_detail,
                "tool_success_rate": 1.0 if not tool_calls_detail else sum(1 for c in tool_calls_detail if c["success"]) / len(tool_calls_detail),
                "fallback_triggered": False
            }

        except Exception as e:
            logger.error(f"Tool Agent execution error: {e}")
            return {
                "answer": f"Agent error: {str(e)}",
                "tools_called": tools_called,
                "tool_calls_detail": tool_calls_detail,
                "tool_success_rate": 0.0,
                "fallback_triggered": True,
                "error": str(e)
            }

    async def aquery(self, question: str) -> str:
        """Process user inquiry asynchronously."""
        return self.query(question)
