import logging
import config
from services.memory_service import MemoryStore
from services.summarization_service import SummarizationService

logger = logging.getLogger(__name__)
memory_store = MemoryStore()

class SummarizationManager:
    _message_counts = {}

    @staticmethod
    def trigger(chat_id, prompt):
        SummarizationManager._message_counts[chat_id] = SummarizationManager._message_counts.get(chat_id, 0) + 1
        
        if SummarizationManager._message_counts[chat_id] >= 10:
            logger.info(
                "[SummarizationManager] Triggering summarization. Chat ID: %s, Message Count: %s",
                chat_id, 
                SummarizationManager._message_counts[chat_id]
            )
            # Fetch recent history (simulated for now)
            # In a real app, fetch conversation history from memory_store
            recent_history = [prompt] 
            summary = SummarizationService.summarize_context(recent_history)
            memory_store.save_summary(chat_id, summary)
            logger.info("[SummarizationManager] Summary saved for Chat ID: %s", chat_id)
            SummarizationManager._message_counts[chat_id] = 0

    @staticmethod
    def get_context(chat_id, prompt):
        context = ""
        # Add existing memory
        relevant_memories = memory_store.search_memory(user_id="user", chat_id=chat_id, query=prompt)
        if relevant_memories:
            context += "\n\nRelevant Context:\n" + "\n".join(relevant_memories)
        
        # Add summary
        summary = memory_store.get_summary(chat_id)
        if summary:
            context += "\n\nConversation Summary:\n" + summary
        return context
