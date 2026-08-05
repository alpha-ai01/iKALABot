import logging
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
    """Route request to the selected provider.

    Behavior:
    - If provider explicitly set to 'gemini' or 'openrouter', call that provider only.
    - If provider == 'auto', prefer OpenRouter (configured to openrouter/free) first,
      with a single retry on transient failure, then fall back to Gemini with a retry.

    Returns: string response (empty string on failure)
    """
    # Explicit provider selected
    if provider == "gemini":
        try:
            return generate_gemini_response(prompt, is_vision=is_vision)
        except Exception as e:
            logging.error("[Router] Gemini error: %s", _redact_exception(e))
            return ""

    if provider == "openrouter":
        try:
            return generate_openrouter_response(prompt, is_x_search=is_x_search)
        except Exception as e:
            logging.error("[Router] OpenRouter error: %s", _redact_exception(e))
            return ""

    # Auto routing: prefer OpenRouter (free) then Gemini
    # Try OpenRouter with one retry
    try:
        response = generate_openrouter_response(prompt, is_x_search=is_x_search)
        if response:
            return response
    except Exception as e:
        logging.error("[Router] OpenRouter attempt failed: %s", _redact_exception(e))

    # Retry once for OpenRouter
    try:
        response = generate_openrouter_response(prompt, is_x_search=is_x_search)
        if response:
            return response
    except Exception as e:
        logging.error("[Router] OpenRouter retry failed: %s", _redact_exception(e))

    # Fallback to Gemini with one attempt + retry
    try:
        response = generate_gemini_response(prompt, is_vision=is_vision)
        if response:
            return response
    except Exception as e:
        logging.error("[Router] Gemini attempt failed: %s", _redact_exception(e))

    try:
        response = generate_gemini_response(prompt, is_vision=is_vision)
        if response:
            return response
    except Exception as e:
        logging.error("[Router] Gemini retry failed: %s", _redact_exception(e))

    # All attempts failed
    logging.error("[Router] All providers failed for prompt (redacted)")
    return ""
