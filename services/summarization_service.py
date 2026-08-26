import logging
import config
from ai.gemini_api import generate_gemini_response

logger = logging.getLogger(__name__)

class SummarizationService:
    @staticmethod
    def summarize_context(messages: list) -> str:
        """Summarize a list of messages into a concise context block."""
        if not messages:
            return ""
        
        prompt = "Summarize the following conversation context in a concise manner, preserving key information:\n\n" + "\n".join(messages)
        
        logger.info("[SummarizationService] Summarizing context...")
        # Using Gemini primary for summarization
        summary = generate_gemini_response(prompt_data=prompt, is_vision=False)
        return summary
