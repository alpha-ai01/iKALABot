import logging
import config
from ai.gateway import AIGateway

logging.basicConfig(level=logging.INFO)

def route_request(
    prompt,
    is_vision=False,
    is_complex=False,
):
    """Route request to the AI Gateway.
    
    The Gateway will handle model selection (free-only) and fallback.
    """
    logging.info("[Router] Starting AI request (Complex: %s, Vision: %s)", is_complex, is_vision)

    capability = "text"
    if is_vision:
        capability = "vision"
    
    # Simple routing to Gateway
    response = AIGateway.call_ai(prompt, capability=capability)
    
    if response and not response.startswith("Error:"):
        return response

    logging.error("[Router] All providers failed")
    return "ขออภัย ระบบ AI ไม่สามารถตอบคำถามได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"

