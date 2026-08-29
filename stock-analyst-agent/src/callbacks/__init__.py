"""
Callbacks for tracking
"""
from langchain_community.callbacks import get_openai_callback
from langchain_core.callbacks import BaseCallbackHandler
from src.constants import PRICING
import time


class MetricsCallback(BaseCallbackHandler):
    """Custom callback for tracking metrics."""
    
    def __init__(self):
        self.start_time = None
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.cost = 0.0
        self.model_name = "gpt-4o"
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.start_time = time.time()
    
    def on_llm_end(self, response, **kwargs):
        if self.start_time:
            self.duration_ms = (time.time() - self.start_time) * 1000
        
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            self.input_tokens = token_usage.get("prompt_tokens", 0)
            self.output_tokens = token_usage.get("completion_tokens", 0)
            self.total_tokens = token_usage.get("total_tokens", 0)
            
            pricing = PRICING.get(self.model_name, PRICING["gpt-4o"])
            self.cost = (
                self.input_tokens * pricing["input"] / 1_000_000
                + self.output_tokens * pricing["output"] / 1_000_000
            )
    
    def get_metrics(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "duration_ms": getattr(self, "duration_ms", 0),
            "cost_usd": self.cost,
        }
