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

    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def handle_text(message):
        text = message.text
        if not text:
            return

        # Simple classification
        task = "chat"
        kwargs = {}

        if any(keyword in text.lower() for keyword in ["กี่โมง", "วันที่", "time", "date"]):
            task = "time"
        elif "ค้นหา" in text:
            task = "search"

        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = execute_task(task, text=text, **kwargs)
            if not response:
                response = "ขออภัยครับ ไม่เข้าใจคำสั่ง"
            bot.reply_to(message, str(response))
        except Exception as e:
            bot.reply_to(message, f"เกิดข้อผิดพลาด: {str(e)}")

    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice_message(message):
        import logging
        logging.info("VOICE_RECEIVED: chat_id=%s", message.chat.id)
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            logging.info("VOICE_FILE_INFO_OK")
            downloaded_file = bot.download_file(file_info.file_path)
            logging.info("VOICE_DOWNLOAD_OK")
            
            from voice.speech_to_text import speech_to_text
            logging.info("VOICE_STT_START")
            transcript = speech_to_text(downloaded_file)
            
            if not transcript:
                logging.info("VOICE_STT_EMPTY")
                bot.reply_to(message, "ขออภัยครับ ไม่สามารถถอดข้อความจากเสียงนี้ได้")
                return
            
            logging.info("VOICE_STT_OK")
            
            # Now process the transcript as a text command
            logging.info("VOICE_DISPATCH_START")
            response = execute_task("chat", text=transcript)
            logging.info("VOICE_DISPATCH_OK")
            
            if not response:
                response = "ขออภัยครับ ไม่เข้าใจคำสั่งในเสียง"
                
            bot.reply_to(message, str(response))
            logging.info("VOICE_REPLY_OK")
        except Exception as e:
            logging.exception("VOICE_STT_FAILED: Error in handle_voice_message")
            bot.reply_to(message, f"เกิดข้อผิดพลาดในการรับข้อความเสียง: เกิดปัญหาภายในระบบ")

    @bot.message_handler(content_types=['photo'])
    def handle_photo_message(message):
        import logging
        logging.info("PHOTO_RECEIVED: chat_id=%s", message.chat.id)
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            # Get the highest resolution photo
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            logging.info("PHOTO_DOWNLOAD_OK")
            downloaded_file = bot.download_file(file_info.file_path)
            logging.info("PHOTO_VALIDATE_OK")
            
            logging.info("VISION_START")
            from ai.gemini_api import generate_gemini_response
            response = generate_gemini_response(downloaded_file, is_vision=True)
            
            if not response:
                logging.info("VISION_EMPTY")
                bot.reply_to(message, "ขออภัยครับ ไม่สามารถวิเคราะห์ภาพนี้ได้")
                return
            
            logging.info("VISION_OK")
            bot.reply_to(message, str(response))
            logging.info("PHOTO_REPLY_OK")
        except Exception as e:
            logging.exception("VISION_FAILED: Error in handle_photo_message")
            bot.reply_to(message, f"เกิดข้อผิดพลาดในการรับภาพ: เกิดปัญหาภายในระบบ")
