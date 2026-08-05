import json
import logging
import requests
import time
import config

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_openrouter_response(prompt, is_x_search=False, retries=2):
    """Call OpenRouter REST API using JSON payload per the provided docs.

    Uses config.DEFAULT_OPENROUTER_MODEL by default (set to openrouter/free),
    or config.DEFAULT_X_SEARCH_MODEL when is_x_search is True.
    Implements simple retry with exponential backoff and redacted logging.
    Returns a stripped string on success or an empty string on failure.
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

    timeout = 20

    for attempt in range(1, retries + 2):
        try:
            # Use requests.json parameter so body is sent as JSON (per docs)
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)

            if resp.status_code != 200:
                body_snippet = resp.text[:1000]
                logging.error("[OpenRouter] non-200 response: %s body=%s", resp.status_code, body_snippet)
            else:
                data = resp.json()
                choices = data.get("choices") or []
                if not choices:
                    return ""

                first = choices[0]
                message = first.get("message") or {}
                content = message.get("content")
                if not content:
                    return ""

                return content.strip()

        except Exception as e:
            logging.error("[OpenRouter] exception attempt %d: %s", attempt, str(e)[:300])

        # Backoff before next attempt
        if attempt <= retries:
            time.sleep(2 ** attempt)

    return ""
