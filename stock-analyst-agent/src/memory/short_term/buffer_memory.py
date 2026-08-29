"""
Short-term memory (custom implementation since langchain.memory is deprecated)
"""
from collections import deque
from typing import Optional


class ShortTermMemory:
    """Short-term conversation memory."""
    
    def __init__(self, k: int = 10, session_id: str = "default"):
        self.session_id = session_id
        self.k = k
        self.messages: deque = deque(maxlen=k * 2)  # *2 for user+assistant pairs
    
    def add_message(self, role: str, content: str):
        """Add a message to memory."""
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self) -> list:
        """Get all messages."""
        return list(self.messages)
    
    def clear(self):
        """Clear memory."""
        self.messages.clear()
    
    def get_memory(self):
        """Get memory object (for compatibility)."""
        return self
