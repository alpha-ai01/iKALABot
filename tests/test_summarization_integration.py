import sqlite3
from services.memory_service import MemoryStore

def test_memory_service():
    # Initialize store which creates tables
    store = MemoryStore("memory.db")
    
    # Test saving and getting a summary
    chat_id = "test_chat_123"
    summary = "This is a test summary."
    store.save_summary(chat_id, summary)
    
    retrieved = store.get_summary(chat_id)
    print(f"Retrieved summary: {retrieved}")
    
    assert retrieved == summary, "Summary retrieval failed!"
    print("Test passed: Summary saved and retrieved successfully.")

if __name__ == "__main__":
    test_memory_service()
