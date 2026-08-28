import logging
import base64
import config
from ai.summarization_manager import SummarizationManager
from ai.openrouter_client import OpenRouterClient
from ai.gemini_api import generate_gemini_response

logger = logging.getLogger(__name__)

class AIGateway:
    @staticmethod
    def _construct_payload(prompt: str, model_id: str, images: list = None, response_format: dict = None):
        # Context is already appended by the caller/router if needed
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        if images:
            for img in images:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                })
            
        payload = {"model": model_id, "messages": messages}
        if response_format:
            payload["response_format"] = response_format
        return payload

    @staticmethod
    def call_ai(prompt: str, capability: str = "text", images: list = None, chat_id: str = None, response_format: dict = None) -> str:
        logger.info(f"[Gateway] Request: capability={capability}, images={bool(images)}")
        
        # 1. Trigger summarization exactly once
        if chat_id:
            SummarizationManager.trigger(chat_id, prompt)
            context = SummarizationManager.get_context(chat_id, prompt)
            full_prompt = prompt + context
        else:
            full_prompt = prompt

        # 2. Routing Logic
        if capability in ["vision", "audio"] or images:
            logger.info("[Router] VISION/AUDIO -> Gemini")
            image_bytes = base64.b64decode(images[0]) if images else None
            return generate_gemini_response(prompt_data=image_bytes or full_prompt, is_vision=bool(images))
        
        # Text Routing
        logger.info("[Router] TEXT -> OpenRouter")
        model_id = config.MODEL_CONFIG["openrouter"]["primary"]
        
        payload = AIGateway._construct_payload(full_prompt, model_id, images, response_format)
        response = OpenRouterClient.call_model(model_id, payload)
        
        if response:
            return response
            
        # Fallback to Gemini
        logger.warning("[Gateway] OpenRouter failed. Falling back to Gemini.")
        return generate_gemini_response(prompt_data=full_prompt, is_vision=False)
