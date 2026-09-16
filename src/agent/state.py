"""
Agent state definitions and data schemas
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document


@dataclass
class AgentState:
    """State of the AI Agent during execution."""
    query: str
    context: Optional[str] = None
    retrieved_documents: List[Document] = field(default_factory=list)
    reranked_documents: List[Document] = field(default_factory=list)
    response: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
