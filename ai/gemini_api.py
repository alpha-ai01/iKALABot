import logging
import config
import os

_client = None

def get_client():
    global _client
    if _client is None:
        from google import genai
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client

def generate_gemini_response(prompt_data, is_vision=False, mime_type="image/jpeg", model_override=None):
    model = model_override or config.GEMINI_MODEL
    
    from google.genai import types

    contents = []
    if is_vision:
        contents.append(types.Part.from_bytes(data=prompt_data, mime_type=mime_type))
        contents.append(types.Part.from_text(text="วิเคราะห์ภาพนี้อย่างละเอียด อธิบายข้อความ วัตถุ และข้อมูลสำคัญที่มองเห็น"))
    else:
        contents.append(types.Part.from_text(text=prompt_data))

    try:
        logging.info("[Gemini] Trying model: %s", model)
        response = get_client().models.generate_content(
            model=model,
            contents=contents,
        )
        logging.info("[Gemini] Success")
        return (response.text or "").strip()
    except Exception as e:
        logging.error("[Gemini] Failed with model %s: %s", model, str(e)[:200])
        return ""

