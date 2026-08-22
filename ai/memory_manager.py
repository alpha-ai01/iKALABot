import logging
import config
from services.memory_service import MemoryStore

class MemoryManager:
    def __init__(self):
        self.store = MemoryStore()
        # Assume Groq client initialization similar to Gemini
        # from groq import Groq
        # self.client = Groq(api_key=config.GROQ_API_KEY)

    def evaluate_and_save(self, user_id, chat_id, text, response):
        """Evaluate if conversation content is worth remembering."""
        logging.info("[Memory] Evaluating memory for user: %s", user_id)
        
        # 1. Ask Groq to analyze text and response for potential memory
        # 2. If Groq suggests memory, call self.store.save_memory()
        
        # Placeholder for actual Groq logic
        pass

    def get_relevant_memories(self, user_id, chat_id, query):
        """Retrieve relevant memories for context."""
        return self.store.search_memory(user_id, chat_id, query)
