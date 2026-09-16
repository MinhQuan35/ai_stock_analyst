"""
General helper functions for AI Agent
"""
import os
from pathlib import Path
from typing import Any, List


def ensure_dir(path: str | Path) -> Path:
    """Ensure directory exists and return Path object."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text for concise logging/display."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
