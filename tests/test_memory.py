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

def test_get_recent_messages():
    db_path = "test_memory_recent.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    memory = MemoryStore(db_path=db_path)
    
    # Save 12 messages for chat1
    for i in range(12):
        memory.save_memory("user1", "chat1", f"msg{i}", "user" if i % 2 == 0 else "assistant", f"message {i}")
    
    # Save 2 messages for chat2
    memory.save_memory("user1", "chat2", "msg100", "user", "message A")
    memory.save_memory("user1", "chat2", "msg101", "assistant", "message B")
    
    # Test chat1: should get last 10 (messages 2-11)
    history1 = memory.get_recent_messages("chat1", limit=10)
    assert len(history1) == 10
    assert history1[0]["text"] == "message 2"
    assert history1[-1]["text"] == "message 11"
    
    # Test chat2: should get 2 messages
    history2 = memory.get_recent_messages("chat2", limit=10)
    assert len(history2) == 2
    assert history2[0]["text"] == "message A"
    assert history2[1]["text"] == "message B"
    
    # Clean up
    if os.path.exists(db_path):
        os.remove(db_path)
