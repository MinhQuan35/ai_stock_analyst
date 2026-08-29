"""
LangChain Metrics - Track cost, tokens, latency
"""
import time
from langchain_community.callbacks import get_openai_callback


class LangChainMetrics:
    """Track metrics for LangChain calls."""
    
    PRICING = {
        "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
        "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    }
    
    def __init__(self):
        self.requests = []
    
    def track(self, func, *args, **kwargs):
        """Track a function call."""
        start = time.time()
        
        with get_openai_callback() as cb:
            result = func(*args, **kwargs)
        
        duration = (time.time() - start) * 1000
        
        metrics = {
            "duration_ms": duration,
            "input_tokens": cb.prompt_tokens,
            "output_tokens": cb.completion_tokens,
            "total_tokens": cb.total_tokens,
            "cost_usd": cb.total_cost,
        }
        
        self.requests.append(metrics)
        return result, metrics
    
    def get_summary(self) -> dict:
        """Get aggregated metrics."""
        if not self.requests:
            return {}
        
        total_cost = sum(r["cost_usd"] for r in self.requests)
        avg_latency = sum(r["duration_ms"] for r in self.requests) / len(self.requests)
        total_input = sum(r["input_tokens"] for r in self.requests)
        total_output = sum(r["output_tokens"] for r in self.requests)
        
        return {
            "total_requests": len(self.requests),
            "total_cost_usd": total_cost,
            "avg_cost_per_request": total_cost / len(self.requests),
            "avg_latency_ms": avg_latency,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
        }
    
    def print_summary(self):
        """Print metrics summary."""
        summary = self.get_summary()
        if not summary:
            print("No metrics recorded")
            return
        
        print("\n" + "=" * 50)
        print("  LANGCHAIN METRICS")
        print("=" * 50)
        print(f"  Total Requests:    {summary['total_requests']}")
        print(f"  Total Cost:        ${summary['total_cost_usd']:.6f}")
        print(f"  Avg Cost/Request:  ${summary['avg_cost_per_request']:.6f}")
        print(f"  Avg Latency:       {summary['avg_latency_ms']:.1f}ms")
        print(f"  Total Input:       {summary['total_input_tokens']:,} tokens")
        print(f"  Total Output:      {summary['total_output_tokens']:,} tokens")
        print("=" * 50)
