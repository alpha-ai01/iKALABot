import sqlite3
import datetime
import os

class MemoryStore:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    chat_id TEXT,
                    text TEXT,
                    category TEXT,
                    importance INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)

    def save_memory(self, user_id, chat_id, text, category="general", importance=1):
        now = datetime.datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories (user_id, chat_id, text, category, importance, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, chat_id, text, category, importance, now, now))

    def search_memory(self, user_id, chat_id, query):
        # Basic keyword search; can be upgraded to vector search later
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT text FROM memories 
                WHERE user_id = ? AND chat_id = ? AND text LIKE ?
                ORDER BY importance DESC, updated_at DESC
                LIMIT 5
            """, (user_id, chat_id, f"%{query}%"))
            return [row[0] for row in cursor.fetchall()]

    def list_memories(self, user_id, chat_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, text, category FROM memories 
                WHERE user_id = ? AND chat_id = ?
            """, (user_id, chat_id))
            return cursor.fetchall()

    def delete_memory(self, user_id, chat_id, memory_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories WHERE id = ? AND user_id = ? AND chat_id = ?", 
                         (memory_id, user_id, chat_id))

    def clear_user_memories(self, user_id, chat_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memories WHERE user_id = ? AND chat_id = ?", 
                         (user_id, chat_id))
