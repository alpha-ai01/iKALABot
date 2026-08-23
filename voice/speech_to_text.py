import os
import requests
import base64
import logging

def speech_to_text(audio_bytes: bytes) -> str:
    """Converts audio bytes to text using OpenRouter API."""
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logging.error("[Voice] OPENROUTER_API_KEY is not set.")
        return "[STT ERROR] API Key missing"
    
    url = "https://openrouter.ai/api/v1/audio/transcriptions"
    
    # Encode audio to base64
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    payload = {
        "model": "openai/whisper-large-v3",
        "input_audio": {
            "data": audio_base64,
            "format": "ogg" # Telegram voice is usually ogg/opus
        }
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://ikalabot.ai",
        "X-Title": "iKALABot"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        text = data.get("text", "")
        logging.info("[Voice] STT success")
        return text
        
    except Exception as e:
        logging.error("[Voice] STT failed: %s", str(e)[:200])
        return "[STT ERROR]"
