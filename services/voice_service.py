import os
import logging
from gtts import gTTS
import tempfile

class VoiceService:
    @staticmethod
    def text_to_speech(text: str) -> str:
        """Converts text to speech with fallback to text if gTTS fails."""
        if not text:
            return ""
        
        try:
            lang = 'th' if any('\u0e00' <= char <= '\u0e7f' for char in text) else 'en'
            
            # Use temp directory for consistent cleanup
            temp_dir = tempfile.gettempdir()
            audio_path = os.path.join(temp_dir, f"voice_{os.urandom(4).hex()}.mp3")
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(audio_path)
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                return audio_path
            
            raise Exception("Generated empty audio file.")
            
        except Exception as e:
            logging.error(f"[VoiceService] TTS failed: {e}. Fallback to text.")
            return "" # Returning empty string triggers text fallback in handlers

    @staticmethod
    def speech_to_text(audio_bytes: bytes, mime_type: str = "audio/ogg") -> str:
        """Placeholder for STT implementation, unified from voice/speech_to_text.py"""
        # Note: Implement actual STT logic here if not already present
        # Or delegate to the existing voice/speech_to_text.py
        from voice.speech_to_text import speech_to_text
        return speech_to_text(audio_bytes, mime_type=mime_type)
