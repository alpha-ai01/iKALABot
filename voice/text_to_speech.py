import os
import logging
import tempfile
from gtts import gTTS

def text_to_speech(text: str) -> str:
    """Converts text to speech and returns the path to the temporary mp3 file."""
    if not text:
        return ""
    
    logging.info("[Voice] TTS started")
    
    try:
        # Determine language (simple heuristic)
        lang = 'th' if any('\u0e00' <= char <= '\u0e7f' for char in text) else 'en'
        
        # Create a temporary file
        fd, audio_path = tempfile.mkstemp(suffix=".mp3", prefix="voice_response_")
        os.close(fd) # Close the file descriptor, gTTS will open it
        
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(audio_path)
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            logging.info("[Voice] TTS file created: %s, size: %d bytes", audio_path, os.path.getsize(audio_path))
            return audio_path
        else:
            logging.error("[Voice] TTS failed: Empty file created")
            return ""
            
    except Exception as e:
        logging.error("[Voice] TTS failed: %s", str(e)[:200])
        return ""
