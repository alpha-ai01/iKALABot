import logging
import config
from ai.gateway import AIGateway
from ai.gemini_api import generate_gemini_response

logging.basicConfig(level=logging.INFO)

def route_request(
    prompt,
    is_vision=False,
    is_complex=False,
):
    """Route request to the AI Gateway, with fallback to Gemini."""
    logging.info("[Router] Starting AI request (Complex: %s, Vision: %s)", is_complex, is_vision)

    capability = "text"
    if is_vision:
        capability = "vision"
    
    # 1. Attempt Primary (OpenRouter)
    try:
        response = AIGateway.call_ai(prompt, capability=capability)
        if response and not response.startswith("Error:"):
            return response
        logging.warning("[Router] OpenRouter failed or returned error.")
    except Exception as e:
        logging.error(f"[Router] OpenRouter exception: {e}")
    
    # 2. Attempt Fallback (Gemini)
    logging.info("[Router] Attempting Gemini fallback...")
    try:
        response = generate_gemini_response(prompt)
        if response:
            return response
        logging.error("[Router] Gemini fallback failed.")
    except Exception as e:
        logging.error(f"[Router] Gemini fallback exception: {e}")

    return "ขออภัย ระบบ AI ไม่สามารถตอบคำถามได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"

