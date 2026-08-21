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
    provider="auto",
    is_vision=False,
    is_x_search=False,
):
    """Route request to the selected provider using the fallback strategy.

    Strategy:
    1. Gemini 3.5 Flash (config.GEMINI_MODEL)
    2. OpenRouter (config.OPENROUTER_MODEL)
    3. Gemini 3.5 Flash-Lite (config.GEMINI_FALLBACK_MODEL)

    Returns: string response (empty string on final failure)
    """
    logging.info("[Router] Starting AI request")

    # 1. Try Gemini 3.5 Flash
    response = generate_gemini_response(prompt, is_vision=is_vision, model_override=config.GEMINI_MODEL)
    if response:
        return response

    # 2. Try OpenRouter
    logging.info("[Router] Trying fallback provider: OpenRouter")
    response = generate_openrouter_response(prompt, is_x_search=is_x_search)
    if response:
        return response

    # 3. Try Gemini 3.5 Flash-Lite
    logging.info("[Router] Trying fallback provider: Gemini Lite")
    response = generate_gemini_response(prompt, is_vision=is_vision, model_override=config.GEMINI_FALLBACK_MODEL)
    if response:
        return response

    # All attempts failed
    logging.error("[Router] All providers failed")
    return "ขออภัย ระบบ AI ไม่สามารถตอบคำถามได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"

