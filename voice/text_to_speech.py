import os
import logging
from openai import OpenAI

def text_to_speech(text: str) -> str:
    """Converts text to speech using OpenAI SDK configured for OpenRouter."""
    if not text:
        return ""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logging.error("[Voice] OPENROUTER_API_KEY is not set.")
        return ""
    
    logging.info("[Voice] TTS started")
    
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "https://ikalabot.ai",
                "X-Title": "iKALABot"
            }
        )
        
        response = client.audio.speech.create(
            model="openai/gpt-4o-mini-tts-2025-12-15",
            input=text,
            voice="alloy"
        )
        
        # Create a temporary file
        import tempfile
        fd, audio_path = tempfile.mkstemp(suffix=".mp3", prefix="voice_response_")
        
        response.stream_to_file(audio_path)
        
        os.close(fd)
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            logging.info("[Voice] TTS file created: %s, size: %d bytes", audio_path, os.path.getsize(audio_path))
            return audio_path
        else:
            logging.error("[Voice] TTS failed: Empty file created")
            return ""
            
    except Exception as e:
        logging.error("[Voice] TTS failed: %s", str(e)[:200])
        return ""
