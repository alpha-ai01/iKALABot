import logging
import config
from ai.gateway import AIGateway

logging.basicConfig(level=logging.INFO)

def route_request(
    prompt,
    is_vision=False,
    is_complex=False,
    images=None,
    chat_id=None
):
    """Route request to the AI Gateway.
    
    The Gateway will handle model selection (free-only) and fallback.
    """
    logging.info("[Router] Starting AI request (Complex: %s, Vision: %s)", is_complex, is_vision)

    capability = "text"
    if is_vision:
        capability = "vision"
    
    # Gateway handles its own fallback
    response = AIGateway.call_ai(prompt, capability=capability, images=images, chat_id=chat_id)
    
    if response and len(response.strip()) > 0:
        return response

    logging.error("[Router] All providers (OpenRouter & Gemini) failed")
    return "ขออภัย ระบบ AI ไม่สามารถตอบคำถามได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"

