"""
Simple Tracer
"""
import time
import uuid
from contextlib import contextmanager
from typing import Optional


class Span:
    """A tracing span."""
    
    def __init__(self, name: str, trace_id: str = None, parent_id: str = None):
        self.name = name
        self.trace_id = trace_id or str(uuid.uuid4())
        self.span_id = str(uuid.uuid4())
        self.parent_id = parent_id
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.metadata: dict = {}
        self.events: list[dict] = []
    
    def set_attribute(self, key: str, value):
        """Set attribute."""
        self.metadata[key] = value
    
    def add_event(self, name: str, **kwargs):
        """Add event."""
        self.events.append({"name": name, "time": time.time(), **kwargs})
    
    def finish(self):
        """Finish span."""
        self.end_time = time.time()
    
    @property
    def duration_ms(self) -> float:
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "events": self.events,
        }


class Tracer:
    """Simple tracer."""
    
    def __init__(self):
        self.spans: list[Span] = []
    
    @contextmanager
    def span(self, name: str, **metadata):
        """Create a span context."""
        s = Span(name)
        s.metadata = metadata
        try:
            yield s
        finally:
            s.finish()
            self.spans.append(s)
    
    def get_spans(self) -> list[dict]:
        """Get all spans as dicts."""
        return [s.to_dict() for s in self.spans]
    
    def clear(self):
        """Clear spans."""
        self.spans.clear()


# Singleton
_tracer = Tracer()


def get_tracer() -> Tracer:
    """Get singleton tracer."""
    return _tracer
