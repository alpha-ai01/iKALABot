import logging
import time
from google import genai
import config

# Initialize Gemini client using config (read from environment via config)
client = genai.Client(api_key=config.GEMINI_API_KEY)


def _prepare_contents(prompt):
    """Prepare contents in a format compatible with the genai SDK.
    If prompt is already a list/dict (pre-built content), return it unchanged.
    Otherwise wrap the string prompt into the expected parts structure.
    """
    if isinstance(prompt, (list, dict)):
        return prompt

    return [{"parts": [{"text": prompt}]}]


def generate_gemini_response(prompt, is_vision=False, retries=2, timeout_seconds=20):
    """Generate text using Gemini via google-genai SDK with simple retry/backoff.

    - prompt: string or prebuilt contents
    - is_vision: whether to use vision model
    - retries: number of retries on failure (total attempts = retries + 1)
    - timeout_seconds: best-effort timeout for each attempt (SDK may not honor)

    Returns a stripped string on success or an empty string on failure.
    """
    model = config.DEFAULT_GEMINI_VISION_MODEL if is_vision else config.DEFAULT_GEMINI_MODEL
    contents = _prepare_contents(prompt)

    for attempt in range(1, retries + 2):
        try:
            # Best-effort: the SDK may not accept a timeout param; keep each attempt bounded
            response = client.models.generate_content(
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
                        try:
                            joined = "".join([p.get("text", "") for p in text.parts])
                            return joined.strip()
                        except Exception:
                            return str(text).strip()
                    return str(text).strip()

            # If we get here, treat as failure and retry
            logging.error("[Gemini] empty response or unexpected shape on attempt %d", attempt)

        except Exception as e:
            # Redact details: log only short exception message
            logging.error("[Gemini] API error attempt %d: %s", attempt, str(e)[:300])

        # Backoff before next attempt
        if attempt <= retries:
            sleep_seconds = 2 ** attempt
            time.sleep(sleep_seconds)

    return ""
