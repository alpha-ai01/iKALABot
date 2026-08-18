import os
import config

_client = None

def get_client():
    global _client
    if _client is None:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=api_key)
    return _client

def speech_to_text(audio_bytes):
    model = config.DEFAULT_GEMINI_MODEL

    response = get_client().models.generate_content(
        model=model,
        contents=[
            "ถอดข้อความจากไฟล์เสียงนี้เป็นข้อความเท่านั้น",
            {
                "mime_type": "audio/ogg",
                "data": audio_bytes,
            },
        ],
    )

    return (response.text or "").strip()
