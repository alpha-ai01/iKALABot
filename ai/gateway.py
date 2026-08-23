import logging
import json
import config
from openai import OpenAI
from ai.model_registry import is_model_free, get_best_free_model

logger = logging.getLogger(__name__)

class AIGateway:
    @staticmethod
    def _get_client():
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=config.OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": "https://ikalabot.ai",
                "X-Title": "iKALABot"
            }
        )

    @staticmethod
    def call_ai(prompt: str, capability: str = "text", images: list = None) -> str:
        """Unified interface for AI requests using OpenAI SDK."""
        logger.info(f"[Gateway] Request: capability={capability}")
        
        # 1. Determine model
        model_id = get_best_free_model(capability)
        if not model_id:
            return "No compatible free model is currently available."
        
        # 2. Pre-request free-model validation (Security enforcement)
        if not is_model_free(model_id):
            logger.error(f"[Gateway] Security violation: Attempted to use non-free model {model_id}")
            return "Security error: Model is not free."
            
        logger.info(f"[Gateway] Using free model: {model_id}")
        
        # 3. Construct payload
        messages = [{"role": "user", "content": prompt}]
        
        # 4. Request with SDK
        try:
            client = AIGateway._get_client()
            response = client.chat.completions.create(
                model=model_id,
                messages=messages
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"[Gateway] Error: {e}")
            return f"Error: {e}"
