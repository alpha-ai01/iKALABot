import telebot
from dispatcher import execute_task
from ai.gemini_api import generate_gemini_response
import config
from utils.response_manager import send_ai_response, set_voice_enabled, init_prefs_db

# Bot instance will be initialized in main.py to avoid circular imports
bot = None

def init_handlers(bot_instance):
    global bot
    bot = bot_instance
    init_prefs_db()

    @bot.message_handler(commands=['voice_on'])
    def voice_on(message):
        set_voice_enabled(message.from_user.id, True)
        bot.reply_to(message, "เปิดใช้งานข้อความเสียงแล้วครับ")

    @bot.message_handler(commands=['voice_off'])
    def voice_off(message):
        set_voice_enabled(message.from_user.id, False)
        bot.reply_to(message, "ปิดใช้งานข้อความเสียงแล้วครับ")

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "สวัสดีครับ ผมคือ iKALABot ผู้ช่วยอัจฉริยะ ยินดีให้บริการครับ มีอะไรให้ผมช่วยดูแลหรือสอบถามเพิ่มเติมได้เลยครับ")

    @bot.message_handler(commands=['memory'])
    def list_memories(message):
        from ai.memory_manager import MemoryManager
        manager = MemoryManager()
        memories = manager.store.list_memories(message.from_user.id, message.chat.id)
        if not memories:
            bot.reply_to(message, "ไม่มีความทรงจำที่ถูกบันทึกไว้ครับ")
            return
        
        response = "ความทรงจำของคุณ:\n"
        for mem in memories:
            response += f"- ID: {mem[0]}, เนื้อหา: {mem[1][:30]}... ({mem[2]})\n"
        bot.reply_to(message, response)

    @bot.message_handler(commands=['forget'])
    def forget_memory(message):
        try:
            memory_id = int(message.text.split()[1])
            from ai.memory_manager import MemoryManager
            manager = MemoryManager()
            manager.store.delete_memory(message.from_user.id, message.chat.id, memory_id)
            bot.reply_to(message, "ลบความทรงจำเรียบร้อยแล้ว")
        except:
            bot.reply_to(message, "กรุณาระบุ ID ความทรงจำที่ต้องการลบ เช่น /forget 1")

    @bot.message_handler(commands=['forget_all'])
    def forget_all_memories(message):
        from ai.memory_manager import MemoryManager
        manager = MemoryManager()
        manager.store.clear_user_memories(message.from_user.id, message.chat.id)
        bot.reply_to(message, "ลบความทรงจำทั้งหมดของคุณแล้ว")

    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def handle_text(message):
        from utils.text_utils import clean_ai_response
        from ai.memory_manager import MemoryManager
        text = message.text
        if not text:
            return
        
        user_id = message.from_user.id
        chat_id = message.chat.id

        # 1. Retrieve relevant memories
        manager = MemoryManager()
        relevant_memories = manager.get_relevant_memories(user_id, chat_id, text)
        
        # Add memories to context if available
        prompt = text
        if relevant_memories:
            prompt = f"ความทรงจำที่เกี่ยวข้อง: {' '.join(relevant_memories)}\n\nคำถาม: {text}"

        # Simple classification
        task = "chat"
        kwargs = {}

        if any(keyword in text.lower() for keyword in ["กี่โมง", "วันที่", "time", "date"]):
            task = "time"
        elif "ค้นหา" in text:
            task = "search"

        try:
            bot.send_chat_action(message.chat.id, 'typing')
            response = execute_task(task, text=prompt, **kwargs)
            if not response:
                response = "ขออภัยครับ ไม่เข้าใจคำสั่ง"
            
            # Centralized response
            send_ai_response(bot, message, response)
            
            # 2. Evaluate and save new memory
            manager.evaluate_and_save(user_id, chat_id, text, str(response))
        except Exception as e:
            bot.reply_to(message, f"เกิดข้อผิดพลาด: {str(e)}")

    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice_message(message):
        import logging
        import os
        from voice.speech_to_text import speech_to_text
        
        logging.info("VOICE_RECEIVED: chat_id=%s", message.chat.id)
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            logging.info("VOICE_FILE_INFO_OK")
            downloaded_file = bot.download_file(file_info.file_path)
            logging.info("VOICE_DOWNLOAD_OK")
            
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
            
            # Centralized response
            send_ai_response(bot, message, response)
            logging.info("VOICE_REPLY_OK")
                
        except Exception as e:
            logging.exception("VOICE_STT_FAILED: Error in handle_voice_message")
            bot.reply_to(message, f"เกิดข้อผิดพลาดในการรับข้อความเสียง: เกิดปัญหาภายในระบบ")

    @bot.message_handler(content_types=['document'])
    def handle_document_message(message):
        import logging
        import os
        from services.document_service import get_file_content
        from ai.gemini_api import generate_gemini_response

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
            
            # Centralized response
            send_ai_response(bot, message, response)
            
        except Exception as e:
            logging.exception("DOCUMENT_FAILED")
            bot.reply_to(message, f"เกิดข้อผิดพลาดในการประมวลผลเอกสาร")
        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logging.info("DOCUMENT_CLEANUP_OK: %s", file_path)
