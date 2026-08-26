import logging
import requests
import json
import config
import base64
from ai.model_registry import is_model_free, get_best_free_model, get_free_models

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
    def _construct_payload(prompt: str, model_id: str, images: list = None):
        if images:
            content = [{"type": "text", "text": prompt}]
            for img in images:
                # Assuming images are already base64 encoded strings
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                })
            messages = [{"role": "user", "content": content}]
        else:
            messages = [{"role": "user", "content": prompt}]
            
        return {"model": model_id, "messages": messages}

    @staticmethod
    def call_ai(prompt: str, capability: str = "text", images: list = None) -> str:
        """Unified interface for AI requests with fallback logic."""
        logger.info(f"[Gateway] Request: capability={capability}")
        
        # 1. Get all available free models for fallback
        free_models = get_free_models()
        model_ids = [m.get("id") for m in free_models]
        
        # 2. Try OpenRouter models one by one
        for model_id in model_ids:
            payload = AIGateway._construct_payload(prompt, model_id, images)
            
            try:
                response = requests.post(
                    OPENROUTER_URL, 
                    headers=AIGateway._get_headers(), 
                    data=json.dumps(payload), 
                    timeout=30
                )
                
                if response.status_code == 429:
                    logger.warning(f"[Gateway] Rate limit on {model_id}. Trying another free model.")
                    continue # Try next model
                
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
            except Exception as e:
                logger.error(f"[Gateway] Error with {model_id}: {e}")
                continue # Try next model
        
        # 3. All OpenRouter models failed. Fallback to Gemini.
        logger.warning("[Gateway] All OpenRouter models failed. Falling back to Gemini.")
        from ai.gemini_api import generate_gemini_response
        
        # Convert base64 images back to bytes if Gemini needs them
        image_bytes = None
        if images:
            # Assuming just one image for now as per handler
            image_bytes = base64.b64decode(images[0])
            
        return generate_gemini_response(prompt, is_vision=bool(images), prompt_data=image_bytes or prompt)
