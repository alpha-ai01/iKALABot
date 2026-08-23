import logging
import requests
import json
import config
from ai.model_registry import is_model_free, get_best_free_model

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class AIGateway:
    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ikalabot.ai",
            "X-Title": "iKALABot"
        }

    @staticmethod
    def call_ai(prompt: str, capability: str = "text", images: list = None) -> str:
        """Unified interface for AI requests."""
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
        # Handle multimodal
        if images:
            # Need to format for OpenRouter (e.g., base64 or URLs)
            # This is a placeholder for actual multimodal construction
            pass
            
        payload = {
            "model": model_id,
            "messages": messages
        }
        
        logger.info(f"[Gateway] Request URL: {OPENROUTER_URL}")
        logger.info(f"[Gateway] Request Payload: {json.dumps(payload)}")
        
        # 4. Request with fallback logic (within free models only)
        try:
            response = requests.post(OPENROUTER_URL, headers=AIGateway._get_headers(), data=json.dumps(payload), timeout=30)
            
            if response.status_code == 429: # Rate limit
                logger.warning(f"[Gateway] Rate limit on {model_id}. Trying another free model.")
                # Implement retry/fallback logic to another free model here
                return "Rate limited. Please try again later."
                
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"[Gateway] Error: {e}")
            return f"Error: {e}"
