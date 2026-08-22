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
        from utils.text_utils import clean_ai_response
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
            
            clean_response = clean_ai_response(str(response))
            bot.reply_to(message, clean_response)
        except Exception as e:
            bot.reply_to(message, f"เกิดข้อผิดพลาด: {str(e)}")

    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice_message(message):
        import logging
        import os
        from voice.text_to_speech import text_to_speech
        from utils.text_utils import clean_ai_response
        
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
            
            clean_response = clean_ai_response(str(response))
                
            # Send text response
            bot.reply_to(message, clean_response)
            logging.info("VOICE_REPLY_OK")
            
            # TTS and send voice
            logging.info("[Voice] TTS started")
            audio_path = text_to_speech(clean_response)
            
            if audio_path:
                logging.info("[Voice] Sending voice to Telegram")
                with open(audio_path, "rb") as audio:
                    bot.send_voice(message.chat.id, audio)
                logging.info("[Voice] Voice sent successfully")
                
                # Cleanup
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                    logging.info("[Voice] Temporary file removed")
            else:
                logging.info("[Voice] Sending text fallback")
                
        except Exception as e:
            logging.exception("VOICE_STT_FAILED: Error in handle_voice_message")
            bot.reply_to(message, f"เกิดข้อผิดพลาดในการรับข้อความเสียง: เกิดปัญหาภายในระบบ")

    @bot.message_handler(content_types=['document'])
    def handle_document_message(message):
        import logging
        import os
        from services.document_service import get_file_content
        from ai.gemini_api import generate_gemini_response
        from utils.text_utils import clean_ai_response

        logging.info("DOCUMENT_RECEIVED: chat_id=%s", message.chat.id)
        
        file_path = None
        try:
            bot.send_chat_action(message.chat.id, 'upload_document')
            
            # Get file info and download
            file_info = bot.get_file(message.document.file_id)
            file_extension = os.path.splitext(message.document.file_name)[1].lower()
            temp_file_name = f"temp_{message.chat.id}_{message.document.file_id}{file_extension}"
            
            downloaded_file = bot.download_file(file_info.file_path)
            with open(temp_file_name, 'wb') as f:
                f.write(downloaded_file)
            file_path = temp_file_name
            
            logging.info("DOCUMENT_DOWNLOAD_OK: %s", temp_file_name)
            
            # Process content
            bot.send_chat_action(message.chat.id, 'typing')
            content, error = get_file_content(file_path)
            
            if error:
                bot.reply_to(message, f"ขออภัยครับ: {error}")
                return
            
            # Prepare prompt
            user_query = message.caption or "ช่วยวิเคราะห์ไฟล์นี้"
            prompt = f"ชื่อไฟล์: {message.document.file_name}\n\nเนื้อหา:\n{content}\n\nคำถาม: {user_query}"
            
            # Analyze
            response = generate_gemini_response(prompt)
            
            if not response:
                bot.reply_to(message, "ขออภัยครับ ไม่สามารถวิเคราะห์ไฟล์นี้ได้")
                return
            
            clean_response = clean_ai_response(str(response))
            bot.reply_to(message, clean_response)
            
        except Exception as e:
            logging.exception("DOCUMENT_FAILED")
            bot.reply_to(message, f"เกิดข้อผิดพลาดในการประมวลผลเอกสาร")
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logging.info("DOCUMENT_CLEANUP_OK: %s", file_path)
