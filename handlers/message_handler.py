import telebot
from dispatcher import execute_task
from ai.gemini_api import generate_gemini_response
import config

# Bot instance will be initialized in main.py to avoid circular imports
bot = None

def init_handlers(bot_instance):
    global bot
    bot = bot_instance

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "สวัสดีครับ ผมคือ iKALABot ผู้ช่วยอัจฉริยะ ยินดีให้บริการครับ มีอะไรให้ผมช่วยดูแลหรือสอบถามเพิ่มเติมได้เลยครับ")

    @bot.message_handler(func=lambda message: True)
    def handle_text(message):
        text = message.text
        if text and any(bad in text.lower() for bad in ["fuck", "ควย", "Hia"]):
            bot.reply_to(message, "กรุณาใช้ถ้อยคำที่สุภาพในการสนทนานะครับ หากคุณมีคำถามหรือต้องการความช่วยเหลือ สามารถสอบถาม iKALABot ได้เลยครับ ยินดีให้บริการครับ")
            return

        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = execute_task("search", prompt=text)
            if not response:
                response = generate_gemini_response(text)
            bot.reply_to(message, str(response))
        except Exception as e:
            bot.reply_to(message, f"เกิดข้อผิดพลาด: {str(e)}")

    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice_message(message):
        try:
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Using placeholder for now, need to check if this is correct
            response = generate_gemini_response(downloaded_file, is_vision=True)
            if not response:
                response = "ขออภัยครับ ไม่สามารถประมวลผลข้อความเสียงนี้ได้"

            bot.reply_to(message, str(response))
        except Exception as e:
            bot.reply_to(message, f"เกิดข้อผิดพลาดในการรับข้อความเสียง: {str(e)}")
