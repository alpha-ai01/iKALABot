import pytest
from services.memory_service import MemoryStore
import os

def test_memory_store():
    db_path = "test_memory.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    memory = MemoryStore(db_path=db_path)
    
    # Test saving memory with new schema
    memory.save_memory("user1", "chat1", "msg1", "user", "Hello", "greeting", 1)
    
    # Test searching memory
    results = memory.search_memory("user1", "chat1", "Hello")
    assert len(results) == 1
    assert results[0]["role"] == "user"
    assert results[0]["text"] == "Hello"
    
    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)
