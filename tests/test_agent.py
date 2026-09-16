"""
Unit tests for AI Agent & RAG Pipeline
"""
import sys
import unittest
from pathlib import Path

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import RAGPipeline, ConversationMemory, AgentState


class TestAgentComponents(unittest.TestCase):
    """Test core agent state and memory."""
    
    def test_conversation_memory(self):
        memory = ConversationMemory(max_history=5)
        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there!")
        
        history = memory.get_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["content"], "Hi there!")
    
    def test_agent_state(self):
        state = AgentState(query="What is P/E?")
        self.assertEqual(state.query, "What is P/E?")
        self.assertIsNone(state.context)
        self.assertEqual(len(state.retrieved_documents), 0)


if __name__ == "__main__":
    unittest.main()
