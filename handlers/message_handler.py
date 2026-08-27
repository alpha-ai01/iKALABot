import telebot
import logging
import os
from dispatcher import execute_task
from utils.response_manager import send_ai_response
from services.voice_service import VoiceService
from services import document_service

# Bot instance will be initialized in main.py
bot = None

def init_handlers(bot_instance):
    global bot
    bot = bot_instance

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        send_ai_response(bot, message, "สวัสดีครับ ผมคือ iKALABot ผู้ช่วยอัจฉริยะ ยินดีให้บริการครับ")

    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def handle_text(message):
        text = message.text
        if not text:
            return

        # Intent classification
        task = "chat"
        # Expanded time/date detection
        time_keywords = ["กี่โมง", "วันที่", "time", "date", "เวลา", "วันนี้", "เดือน", "ปี", "พ.ศ.", "วัน"]
        if any(k in text.lower() for k in time_keywords):
            task = "time"
        elif "ค้นหา" in text:
            task = "search"

        bot.send_chat_action(message.chat.id, 'typing')
        response = execute_task(task, text=text, chat_id=str(message.chat.id))
        send_ai_response(bot, message, str(response))

    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        logging.info("DOCUMENT_RECEIVED")
        temp_file_path = None
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            # Save downloaded bytes to a temporary file for processing
            file_extension = os.path.splitext(message.document.file_name)[1].lower()
            temp_file_path = f"temp_{message.chat.id}_{message.document.file_id}{file_extension}"
            with open(temp_file_path, 'wb') as f:
                f.write(downloaded)
            
            # Use document service to process
            content = document_service.process_document(temp_file_path)
            
            if content == "รูปแบบไฟล์ไม่รองรับ":
                send_ai_response(bot, message, "ขออภัยครับ รูปแบบไฟล์ไม่รองรับ")
                return
                
            # Form prompt with caption if provided, or default to asking for analysis
            user_query = message.caption or "ช่วยสรุปหรือวิเคราะห์ไฟล์นี้"
            prompt = f"ชื่อไฟล์: {message.document.file_name}\n\nเนื้อหา:\n{content}\n\nคำถาม: {user_query}"
            
            response = execute_task("chat", text=prompt, chat_id=str(message.chat.id))
            send_ai_response(bot, message, str(response))
        except Exception as e:
            logging.exception("DOCUMENT_FAILED")
            send_ai_response(bot, message, "เกิดข้อผิดพลาดในการประมวลผลเอกสาร")
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass

    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice(message):
        logging.info("VOICE_RECEIVED")
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded = bot.download_file(file_info.file_path)
            transcript = VoiceService.speech_to_text(downloaded)
            
            if not transcript:
                send_ai_response(bot, message, "ไม่สามารถถอดเสียงได้")
                return
            
            response = execute_task("chat", text=transcript, chat_id=str(message.chat.id))
            send_ai_response(bot, message, str(response))
        except Exception as e:
            logging.exception("VOICE_FAILED")
            send_ai_response(bot, message, "เกิดข้อผิดพลาดในการรับเสียง")

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        logging.info("PHOTO_RECEIVED")
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            import base64
            img_b64 = base64.b64encode(downloaded).decode('utf-8')
            
            response = execute_task("chat", text="วิเคราะห์ภาพนี้", images=[img_b64], chat_id=str(message.chat.id))
            send_ai_response(bot, message, str(response))
        except Exception as e:
            logging.exception("VISION_FAILED")
            send_ai_response(bot, message, "เกิดข้อผิดพลาดในการวิเคราะห์ภาพ")
