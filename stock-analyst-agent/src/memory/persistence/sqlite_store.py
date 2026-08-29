"""
SQLite-based memory persistence
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional
from datetime import datetime


class SQLiteMemoryStore:
    """Persistent memory store using SQLite."""
    
    def __init__(self, db_path: str = "./data/memory.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity TEXT NOT NULL,
                    attribute TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def save_message(self, session_id: str, role: str, content: str, metadata: dict = None):
        """Save a message."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
                (session_id, role, content, json.dumps(metadata or {})),
            )
            conn.commit()
    
    def get_messages(self, session_id: str, limit: int = 50) -> list[dict]:
        """Get messages for session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content, metadata, created_at FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            )
            return [
                {"role": row[0], "content": row[1], "metadata": json.loads(row[2] or "{}"), "created_at": row[3]}
                for row in cursor.fetchall()
            ][::-1]
    
    def save_fact(self, entity: str, attribute: str, value: str, confidence: float = 1.0):
        """Save a fact."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO facts (entity, attribute, value, confidence) VALUES (?, ?, ?, ?)",
                (entity, attribute, value, confidence),
            )
            conn.commit()
    
    def get_facts(self, entity: str) -> list[dict]:
        """Get facts for entity."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT attribute, value, confidence, created_at FROM facts WHERE entity = ?",
                (entity,),
            )
            return [
                {"attribute": row[0], "value": row[1], "confidence": row[2], "created_at": row[3]}
                for row in cursor.fetchall()
            ]
