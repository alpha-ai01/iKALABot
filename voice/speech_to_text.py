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
    model = config.VOICE_GEMINI_MODEL
    from google.genai import types
    import logging

    logging.info("[Voice] Using model: %s", model)
    logging.info("[Voice] Gemini request started")
    
    try:
        response = get_client().models.generate_content(
            model=model,
            contents=[
                types.Part.from_text(text="ถอดข้อความจากไฟล์เสียงนี้เป็นข้อความเท่านั้น ตอบเฉพาะข้อความที่ถอดได้"),
                types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg")
            ],
        )
        logging.info("[Voice] Gemini response success")
        return (response.text or "").strip()
    except Exception as e:
        logging.error("[Voice] Gemini API error: %s", str(e)[:200])
        return ""

