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
            # Ensure model is in the payload as per OpenRouter docs
            payload["model"] = model_id
            
            response = requests.post(
                OPENROUTER_URL, 
                headers=OpenRouterClient._get_headers(), 
                data=json.dumps(payload), 
                timeout=30
            )

            if response.status_code == 429:
                logger.warning("[OpenRouterClient] Rate limited on model: %s", model_id)
                return None

            response.raise_for_status()
            data = response.json()

            # Success, reset failures
            OpenRouterClient._model_failures[model_id] = 0
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error("[OpenRouterClient] Error with model: %s. Error: %s", model_id, str(e)[:100])
            
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code in [404, 403]:
                    OpenRouterClient._model_failures[model_id] = OpenRouterClient._model_failures.get(model_id, 0) + 1
                    if OpenRouterClient._model_failures[model_id] >= OpenRouterClient.FAILURE_THRESHOLD:
                        remove_model_from_cache(model_id)
            return None
