from services.voice_service import process_voice_message

def handle(bot, message):
    return process_voice_message(bot, message)
