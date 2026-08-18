import logging
import config

_client = None

def get_client():
    global _client
    if _client is None:
        from google import genai
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _prepare_contents(prompt):
    """Prepare contents in a format compatible with the genai SDK.
    If prompt is already a list/dict (pre-built content), return it unchanged.
    Otherwise wrap the string prompt into the expected parts structure.
    """
    if isinstance(prompt, (list, dict)):
        return prompt

    return [{"parts": [{"text": prompt}]}]


def generate_gemini_response(prompt, is_vision=False):
    model = (
        config.DEFAULT_GEMINI_VISION_MODEL if is_vision else config.DEFAULT_GEMINI_MODEL
    )

    contents = _prepare_contents(prompt)

    try:
        response = get_client().models.generate_content(
            model=model,
            contents=contents,
        )

        # The SDK exposes response.text convenience in many examples.
        text = getattr(response, "text", None)
        if text:
            return (text or "").strip()

        # Fallback: try to extract from candidates/candidates[0].content
        candidates = getattr(response, "candidates", None)
        if candidates and len(candidates) > 0:
            first = candidates[0]
            text = getattr(first, "content", None)
            if text:
                # content may be complex; try to join text parts
                if hasattr(text, "parts"):
                    joined = "".join([p.get("text", "") for p in text.parts])
                    return joined.strip()
                return str(text).strip()

        return ""

    except Exception as e:
        # Log a short redacted error without exposing sensitive details
        logging.error("[Gemini] API error: %s", str(e)[:200])
        return ""
