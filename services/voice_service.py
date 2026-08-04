from voice.speech_to_text import speech_to_text
from dispatcher import execute_task

def process_voice_message(bot, message):
    try:
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        file_info = bot.get_file(file_id)
        audio = bot.download_file(file_info.file_path)

        text = speech_to_text(audio)

        if not text:
            return "ไม่สามารถถอดเสียงได้"

        return execute_task("chat", text)

    except Exception as e:
        return f"Voice Error: {e}"
