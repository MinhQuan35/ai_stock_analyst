"""
Memory module for tracking conversation context and user session history
"""
from typing import List, Dict, Any


class ConversationMemory:
    """In-memory chat history manager."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """Add user or assistant message to memory."""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]
    
    def get_history(self) -> List[Dict[str, str]]:
        """Retrieve full conversation history."""
        return self.history
    
    def clear(self):
        """Clear memory."""
        self.history.clear()
