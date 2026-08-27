import telebot
import logging
import os
import tempfile
from dispatcher import execute_task
from utils.response_manager import send_ai_response
from services.voice_service import VoiceService
from services import document_service

# Bot instance will be initialized in main.py
bot = None

def handle_document(message):
    logging.info("DOCUMENT_RECEIVED")
    
    SAFE_LIMIT_MB = 19
    SAFE_LIMIT_BYTES = SAFE_LIMIT_MB * 1024 * 1024
    
    # 1. Pre-check file size if available
    file_size = message.document.file_size
    if file_size and file_size > SAFE_LIMIT_BYTES:
        error_msg = f"ขออภัยครับ ไฟล์ใหญ่เกินขนาดที่ระบบรับได้ (ได้รับ {round(file_size/(1024*1024), 2)} MB, จำกัดที่ {SAFE_LIMIT_MB} MB). กรุณาแบ่งไฟล์หรือลดขนาดก่อนส่งครับ"
        logging.warning(f"DOCUMENT_REJECTED_FILE_TOO_LARGE: {file_size} bytes (Limit: {SAFE_LIMIT_BYTES} bytes)")
        send_ai_response(bot, message, error_msg)
        return

    try:
        bot.send_chat_action(message.chat.id, 'typing')
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        # Create a secure temporary file
        file_extension = os.path.splitext(message.document.file_name)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            tmp.write(downloaded)
            temp_file_path = tmp.name
        
        # Use document service to process
        content_chunks = document_service.process_document(temp_file_path)
        
        if content_chunks == ["รูปแบบไฟล์ไม่รองรับ"]:
            send_ai_response(bot, message, "ขออภัยครับ รูปแบบไฟล์ไม่รองรับ")
            return
            
        # Process each chunk
        for i, chunk in enumerate(content_chunks):
            user_query = message.caption or "ช่วยสรุปหรือวิเคราะห์ไฟล์นี้"
            if len(content_chunks) > 1:
                prompt = f"ชื่อไฟล์: {message.document.file_name} (ส่วนที่ {i+1}/{len(content_chunks)})\n\nเนื้อหา:\n{chunk}\n\nคำถาม: {user_query} (โปรดวิเคราะห์ส่วนนี้)"
            else:
                prompt = f"ชื่อไฟล์: {message.document.file_name}\n\nเนื้อหา:\n{chunk}\n\nคำถาม: {user_query}"
            
            response = execute_task("chat", text=prompt, chat_id=str(message.chat.id))
            send_ai_response(bot, message, str(response))
    except telebot.apihelper.ApiTelegramException as e:
        if "file is too big" in str(e).lower():
            error_msg = f"ขออภัยครับ ไฟล์ใหญ่เกินขนาดที่ Bot ดาวน์โหลดได้ ({SAFE_LIMIT_MB} MB). กรุณาแบ่งไฟล์หรือลดขนาดก่อนส่งครับ"
            logging.warning(f"DOCUMENT_REJECTED_FILE_TOO_LARGE_API: {str(e)}")
            send_ai_response(bot, message, error_msg)
        else:
            logging.exception("DOCUMENT_FAILED")
            send_ai_response(bot, message, "เกิดข้อผิดพลาดในการประมวลผลเอกสาร")
    except Exception as e:
        logging.exception("DOCUMENT_FAILED")
        send_ai_response(bot, message, "เกิดข้อผิดพลาดในการประมวลผลเอกสาร")
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

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
    def handle_document_wrapper(message):
        handle_document(message)

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
