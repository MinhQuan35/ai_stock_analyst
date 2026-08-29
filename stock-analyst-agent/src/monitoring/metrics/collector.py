"""
Metrics Collector
"""
import time
from collections import defaultdict
from src.constants import PRICING


class MetricsCollector:
    """Collect and aggregate metrics."""
    
    def __init__(self):
        self.requests: list[dict] = []
    
    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration_ms: float,
        satisfaction: float = None,
        error: str = None,
    ):
        """Record a request."""
        pricing = PRICING.get(model, PRICING["gpt-4o"])
        cost = (input_tokens * pricing["input"] / 1_000_000) + (output_tokens * pricing["output"] / 1_000_000)
        
        self.requests.append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_ms": duration_ms,
            "cost_usd": cost,
            "satisfaction": satisfaction,
            "error": error,
            "timestamp": time.time(),
        })
    
    def get_summary(self) -> dict:
        """Get summary metrics."""
        if not self.requests:
            return {}
        
        total_cost = sum(r["cost_usd"] for r in self.requests)
        latencies = sorted([r["duration_ms"] for r in self.requests])
        n = len(latencies)
        
        return {
            "total_requests": len(self.requests),
            "total_cost_usd": total_cost,
            "avg_cost_per_request": total_cost / n,
            "avg_latency_ms": sum(latencies) / n,
            "p50_latency_ms": latencies[int(n * 0.5)] if n > 0 else 0,
            "p95_latency_ms": latencies[int(n * 0.95)] if n > 0 else 0,
            "p99_latency_ms": latencies[int(n * 0.99)] if n > 0 else 0,
            "total_input_tokens": sum(r["input_tokens"] for r in self.requests),
            "total_output_tokens": sum(r["output_tokens"] for r in self.requests),
            "error_rate": sum(1 for r in self.requests if r["error"]) / n,
        }
    
    def print_summary(self):
        """Print summary."""
        s = self.get_summary()
        if not s:
            print("No metrics")
            return
        
        print("\n" + "=" * 50)
        print("  METRICS SUMMARY")
        print("=" * 50)
        for k, v in s.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.4f}")
            else:
                print(f"  {k}: {v}")
        print("=" * 50)


# Singleton
_collector = None


def get_collector() -> MetricsCollector:
    """Get singleton metrics collector."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector
