import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def speech_to_text(audio_bytes):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                "ถอดข้อความจากไฟล์เสียงนี้เป็นข้อความภาษาเดิมเท่านั้น",
                {
                    "mime_type": "audio/ogg",
                    "data": audio_bytes,
                },
            ],
        )
        return (response.text or "").strip()
    except Exception as e:
        return f"[STT ERROR] {e}"
