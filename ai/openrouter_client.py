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
        logger.info("[OpenRouterClient] Attempting request with model: %s", model_id)
        try:
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
            logger.info("[OpenRouterClient] Success with model: %s", model_id)

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(
                "[OpenRouterClient] Error with model: %s. Failure count: %s. Error: %s",
                model_id,
                OpenRouterClient._model_failures.get(model_id, 0) + 1,
                str(e)[:100]
            )
            if "404" in str(e) or "403" in str(e):
                OpenRouterClient._model_failures[model_id] = OpenRouterClient._model_failures.get(model_id, 0) + 1
                if OpenRouterClient._model_failures[model_id] >= OpenRouterClient.FAILURE_THRESHOLD:
                    logger.critical("[OpenRouterClient] Pruning model due to persistent failures: %s", model_id)
                    remove_model_from_cache(model_id)
                    if model_id in OpenRouterClient._model_failures:
                        del OpenRouterClient._model_failures[model_id]
            return None

