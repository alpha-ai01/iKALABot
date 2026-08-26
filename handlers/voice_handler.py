from services.voice_service import VoiceService
from voice.speech_to_text import speech_to_text

def handle(bot, message):
    # This is a simplified handler structure. Assuming it gets audio bytes from message.
    # Adjust based on the actual Telegram bot library structure if needed.
    audio_path = bot.download_file(message.voice.file_id)
    with open(audio_path, 'rb') as f:
        audio_bytes = f.read()
    
    text = speech_to_text(audio_bytes)
    # Process text using existing AI logic...
    return bot.reply_to(message, text)
