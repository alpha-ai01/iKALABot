import telebot
import logging
import os
from dispatcher import execute_task
from utils.text_utils import clean_ai_response
from services.voice_service import VoiceService

# Bot instance will be initialized in main.py
bot = None

def init_handlers(bot_instance):
    global bot
    bot = bot_instance

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "สวัสดีครับ ผมคือ iKALABot ผู้ช่วยอัจฉริยะ ยินดีให้บริการครับ")

    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def handle_text(message):
        text = message.text
        if not text:
            return

        # Intent classification
        task = "chat"
        if any(k in text.lower() for k in ["กี่โมง", "วันที่", "time", "date"]):
            task = "time"
        elif "ค้นหา" in text:
            task = "search"

        bot.send_chat_action(message.chat.id, 'typing')
        response = execute_task(task, text=text, chat_id=str(message.chat.id))
        bot.reply_to(message, clean_ai_response(str(response)))

    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice(message):
        logging.info("VOICE_RECEIVED")
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            # Extract and convert
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded = bot.download_file(file_info.file_path)
            transcript = VoiceService.speech_to_text(downloaded)
            
            if not transcript:
                bot.reply_to(message, "ไม่สามารถถอดเสียงได้")
                return
            
            # Unified execution
            response = execute_task("chat", text=transcript, chat_id=str(message.chat.id))
            clean_response = clean_ai_response(str(response))
            bot.reply_to(message, clean_response)
            
            # Voice reply
            audio_path = VoiceService.text_to_speech(clean_response)
            if audio_path:
                with open(audio_path, "rb") as f:
                    bot.send_voice(message.chat.id, f)
                os.remove(audio_path)
        except Exception as e:
            logging.exception("VOICE_FAILED")
            bot.reply_to(message, "เกิดข้อผิดพลาดในการรับเสียง")

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        logging.info("PHOTO_RECEIVED")
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            # Get photo
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            # Pass to unified router with image data
            import base64
            img_b64 = base64.b64encode(downloaded).decode('utf-8')
            
            response = execute_task("chat", text="วิเคราะห์ภาพนี้", images=[img_b64], chat_id=str(message.chat.id))
            bot.reply_to(message, clean_ai_response(str(response)))
            
        except Exception as e:
            logging.exception("VISION_FAILED")
            bot.reply_to(message, "เกิดข้อผิดพลาดในการวิเคราะห์ภาพ")
