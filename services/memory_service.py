import sqlite3
import datetime
import os

class MemoryStore:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Table for individual messages/memories
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    chat_id TEXT,
                    message_id TEXT,
                    role TEXT,
                    text TEXT,
                    category TEXT,
                    importance INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Idempotent migration to ensure columns exist
            columns = [info[1] for info in conn.execute("PRAGMA table_info(memories)")]
            if 'message_id' not in columns:
                conn.execute("ALTER TABLE memories ADD COLUMN message_id TEXT")
            if 'role' not in columns:
                conn.execute("ALTER TABLE memories ADD COLUMN role TEXT")

            # Table for conversation summaries
            conn.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    chat_id TEXT PRIMARY KEY,
                    summary TEXT,
                    updated_at TIMESTAMP
                )
            """)

    def save_summary(self, chat_id, summary):
        now = datetime.datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO summaries (chat_id, summary, updated_at)
                VALUES (?, ?, ?)
            """, (chat_id, summary, now))

    def get_summary(self, chat_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT summary FROM summaries WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            return row[0] if row else None

    def save_memory(self, user_id, chat_id, message_id, role, text, category="general", importance=1):
        now = datetime.datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories (user_id, chat_id, message_id, role, text, category, importance, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, chat_id, message_id, role, text, category, importance, now))

    def get_recent_messages(self, chat_id, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT role, text FROM memories 
                WHERE chat_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (chat_id, limit))
            rows = cursor.fetchall()
            return [{"role": row[0], "text": row[1]} for row in reversed(rows)]

    def search_memory(self, user_id, chat_id, query):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT role, text FROM memories 
                WHERE user_id = ? AND chat_id = ? AND text LIKE ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (user_id, chat_id, f"%{query}%"))
            return [{"role": row[0], "text": row[1]} for row in cursor.fetchall()]

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

