import os
import logging
from openai import OpenAI

def speech_to_text(audio_bytes: bytes) -> str:
    """Converts audio bytes to text using OpenAI SDK configured for OpenRouter."""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logging.error("[Voice] OPENROUTER_API_KEY is not set.")
        return "[STT ERROR] API Key missing"
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://ikalabot.ai",
                "X-Title": "iKALABot"
            }
        )
        
        # Create a temporary file to wrap bytes for the SDK
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=True) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio.flush()
            temp_audio.seek(0)
            
            transcript = client.audio.transcriptions.create(
                model="openai/whisper-large-v3",
                file=temp_audio
            )
            
        logging.info("[Voice] STT success")
        return transcript.text
        
    except Exception as e:
        logging.error("[Voice] STT failed: %s", str(e)[:200])
        return "[STT ERROR]"
