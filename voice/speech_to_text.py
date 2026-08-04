import os
import config
from google import genai

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def speech_to_text(audio_bytes):
    response = client.models.generate_content(
        model=config.DEFAULT_GEMINI_MODEL,
        contents=[
            "ถอดข้อความจากไฟล์เสียงนี้เป็นข้อความเท่านั้น",
            {
                "mime_type": "audio/ogg",
                "data": audio_bytes,
            },
        ],
    )

    return (response.text or "").strip()
