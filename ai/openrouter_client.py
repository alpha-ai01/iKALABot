import logging
import requests
import json
import config
from ai.model_registry import remove_model_from_cache

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

class OpenRouterClient:
    _model_failures = {}
    FAILURE_THRESHOLD = 3

    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ikalabot.ai",
            "X-Title": "iKALABot"
        }

    @staticmethod
    def call_model(model_id, payload):
        try:
            response = requests.post(
                OPENROUTER_URL, 
                headers=OpenRouterClient._get_headers(), 
                data=json.dumps(payload), 
                timeout=30
            )
            
            if response.status_code == 429:
                logger.warning(f"[OpenRouterClient] Rate limit on {model_id}.")
                return None
            
            response.raise_for_status()
            data = response.json()
            
            # Success, reset failures
            OpenRouterClient._model_failures[model_id] = 0
            
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"[OpenRouterClient] Error with {model_id}: {e}")
            if "404" in str(e) or "403" in str(e):
                OpenRouterClient._model_failures[model_id] = OpenRouterClient._model_failures.get(model_id, 0) + 1
                if OpenRouterClient._model_failures[model_id] >= OpenRouterClient.FAILURE_THRESHOLD:
                    remove_model_from_cache(model_id)
                    if model_id in OpenRouterClient._model_failures:
                        del OpenRouterClient._model_failures[model_id]
            return None
