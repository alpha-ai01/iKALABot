import logging
import config
from ai.gemini_api import generate_gemini_response
from ai.openrouter_api import generate_openrouter_response


logging.basicConfig(level=logging.INFO)


def _redact_exception(e):
    # Short redacted exception message to avoid leaking sensitive info
    try:
        s = str(e)
        return s[:200]
    except Exception:
        return "<error>"


def route_request(
    prompt,
    is_vision=False,
    is_complex=False,
):
    """Route request to the selected provider using the fallback strategy.

    Strategy:
    1. Complex Task? -> OpenRouter Reasoning
    2. Primary -> Gemini 3.1 Flash-Lite
    3. Fallback -> Gemini 3.5 Flash-Lite (via config.MODEL_CONFIG["GOOGLE"]["fallback"])

    Returns: string response (empty string on final failure)
    """
    logging.info("[Router] Starting AI request (Complex: %s)", is_complex)

    # 1. Try Complex Task -> OpenRouter Reasoning
    if is_complex:
        logging.info("[Router] Routing to OpenRouter Reasoning")
        response = generate_openrouter_response(prompt, is_reasoning=True)
        if response:
            return response

    # 2. Try Primary -> Gemini 3.1 Flash-Lite
    response = generate_gemini_response(prompt, is_vision=is_vision, model_override=config.MODEL_CONFIG["GOOGLE"]["primary"])
    if response:
        return response

    # 3. Try Fallback -> Gemini 3.5 Flash-Lite
    logging.info("[Router] Trying fallback provider: Gemini Lite")
    response = generate_gemini_response(prompt, is_vision=is_vision, model_override=config.MODEL_CONFIG["GOOGLE"]["fallback"])
    if response:
        return response

    # All attempts failed
    logging.error("[Router] All providers failed")
    return "ขออภัย ระบบ AI ไม่สามารถตอบคำถามได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"

