import os
import requests
import logging
import tempfile

def text_to_speech(text: str) -> str:
    """Converts text to speech using OpenRouter API and returns the path to the temporary mp3 file."""
    if not text:
        return ""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logging.error("[Voice] OPENROUTER_API_KEY is not set.")
        return ""
    
    logging.info("[Voice] TTS started")
    
    url = "https://openrouter.ai/api/v1/audio/speech"
    
    payload = {
        "model": "openai/gpt-4o-mini-tts-2025-12-15",
        "input": text,
        "voice": "alloy",
        "response_format": "mp3"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ikalabot.ai",
        "X-Title": "iKALABot"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        response.raise_for_status()
        
        # Create a temporary file
        fd, audio_path = tempfile.mkstemp(suffix=".mp3", prefix="voice_response_")
        
        with open(audio_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
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
