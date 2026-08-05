import json
import logging
import requests
import config

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_openrouter_response(prompt, is_x_search=False):
    """Call OpenRouter REST API using the OpenRouter endpoint described in the project docs.

    Uses config.DEFAULT_OPENROUTER_MODEL by default (set to openrouter/free),
    or config.DEFAULT_X_SEARCH_MODEL when is_x_search is True.
    Returns a safe stripped string on success or an empty string on failure.
    """
    model = config.DEFAULT_X_SEARCH_MODEL if is_x_search else config.DEFAULT_OPENROUTER_MODEL

    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=15)
        if resp.status_code != 200:
            logging.error("[OpenRouter] non-200 response: %s", resp.status_code)
            return ""

        data = resp.json()
        # Per the provided docs: data.choices[0].message.content
        choices = data.get("choices") or []
        if not choices:
            return ""

        first = choices[0]
        message = first.get("message") or {}
        content = message.get("content")
        if not content:
            # Some OpenRouter responses may use 'text' or other shapes; attempt common fallbacks
            # but do not make external assumptions beyond provided docs.
            return ""

        return content.strip()

    except Exception as e:
        # Redact details: log only short exception message
        logging.error("[OpenRouter] API error: %s", str(e)[:200])
        return ""
