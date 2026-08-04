import os
from google import genai
import config

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_gemini_response(prompt, is_vision=False):
    model = (
        config.DEFAULT_GEMINI_VISION_MODEL
        if is_vision
        else config.DEFAULT_GEMINI_MODEL
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return (response.text or "").strip()
