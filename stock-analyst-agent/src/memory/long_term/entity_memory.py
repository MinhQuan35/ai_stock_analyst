"""
Long-term memory for entities and facts
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EntityFact(BaseModel):
    """A fact about an entity."""
    entity: str
    attribute: str
    value: str
    confidence: float = 1.0
    source: str = "conversation"
    created_at: datetime = Field(default_factory=datetime.now)


class LongTermMemory:
    """Long-term entity memory."""
    
    def __init__(self):
        self.facts: list[EntityFact] = []
        self.user_preferences: dict = {}
    
    def add_fact(self, entity: str, attribute: str, value: str, confidence: float = 1.0):
        """Add a fact."""
        self.facts.append(EntityFact(
            entity=entity,
            attribute=attribute,
            value=value,
            confidence=confidence,
        ))
    
    def get_facts(self, entity: str) -> list[EntityFact]:
        """Get facts for an entity."""
        return [f for f in self.facts if f.entity == entity]
    
    def set_preference(self, key: str, value):
        """Set user preference."""
        self.user_preferences[key] = value
    
    def get_preference(self, key: str, default=None):
        """Get user preference."""
        return self.user_preferences.get(key, default)
    
    def search(self, query: str) -> list[EntityFact]:
        """Search facts."""
        query_lower = query.lower()
        return [
            f for f in self.facts
            if query_lower in f.entity.lower()
            or query_lower in f.attribute.lower()
            or query_lower in f.value.lower()
        ]
    
    def clear(self):
        """Clear all memory."""
        self.facts.clear()
        self.user_preferences.clear()
