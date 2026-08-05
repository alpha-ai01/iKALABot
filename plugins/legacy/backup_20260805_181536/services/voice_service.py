from voice.speech_to_text import speech_to_text
from dispatcher import execute_task


def process_voice_message(bot, message):
    try:
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        file_info = bot.get_file(file_id)
        audio = bot.download_file(file_info.file_path)

        text = speech_to_text(audio)

        if not text or text.startswith("[STT ERROR]"):
            return "ขออภัยครับ ไม่สามารถถอดเสียงได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"

        reply = execute_task("chat", text)

        if not reply:
            reply = "ผมไม่สามารถสร้างคำตอบได้"

        return reply

    except Exception as e:
        return f"Voice Error: {e}"
