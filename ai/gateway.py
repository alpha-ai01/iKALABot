import logging
import base64
from ai.model_registry import get_free_models
from ai.summarization_manager import SummarizationManager
from ai.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)

class AIGateway:
    @staticmethod
    def _construct_payload(prompt: str, model_id: str, images: list = None, chat_id: str = None):
        final_prompt = prompt + SummarizationManager.get_context(chat_id, prompt)
        
        # 2. Payload Construction
        if images:
            content = [{"type": "text", "text": final_prompt}]
            for img in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                })
            messages = [{"role": "user", "content": content}]
        else:
            messages = [{"role": "user", "content": final_prompt}]
            
        return {"model": model_id, "messages": messages}

    @staticmethod
    def call_ai(prompt: str, capability: str = "text", images: list = None, chat_id: str = None) -> str:
        logger.info(f"[Gateway] Request: capability={capability}")
        
        # 1. Get all available free models for fallback
        free_models = get_free_models()
        model_ids = [m.get("id") for m in free_models]
        
        # 2. Try OpenRouter models one by one
        for model_id in model_ids:
            if chat_id:
                SummarizationManager.trigger(chat_id, prompt)
            
            payload = AIGateway._construct_payload(prompt, model_id, images, chat_id)
            
            response = OpenRouterClient.call_model(model_id, payload)
            if response:
                return response
                
        # 3. All OpenRouter models failed. Fallback to Gemini.
        logger.warning("[Gateway] All OpenRouter models failed. Falling back to Gemini.")
        from ai.gemini_api import generate_gemini_response
        
        # Convert base64 images back to bytes if Gemini needs them
        image_bytes = None
        if images:
            image_bytes = base64.b64decode(images[0])
            
        return generate_gemini_response(prompt_data=image_bytes or prompt, is_vision=bool(images))
