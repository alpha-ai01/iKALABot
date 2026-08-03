import os
import threading
import http.server
import socketserver
import telebot
from google import genai
import requests
import json
from datetime import datetime
import logging
from bs4 import BeautifulSoup

# ==========================================
# 1. ตั้งค่า Environment Variables & ความปลอดภัย
# ==========================================
PORT = int(os.environ.get("PORT", 8080))
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ระบบซ่อน API Key ไม่ให้หลุดไปใน Log (Safe Logging)
class SafeLogFormatter(logging.Formatter):
    def format(self, record):
        log_msg = super().format(record)
        if TELEGRAM_BOT_TOKEN: log_msg = log_msg.replace(TELEGRAM_BOT_TOKEN, "[HIDDEN_BOT_TOKEN]")
        if OPENROUTER_API_KEY: log_msg = log_msg.replace(OPENROUTER_API_KEY, "[HIDDEN_OR_KEY]")
        if GEMINI_API_KEY: log_msg = log_msg.replace(GEMINI_API_KEY, "[HIDDEN_GEMINI_KEY]")
        return log_msg

logger = logging.getLogger("iKALABot")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(SafeLogFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# ==========================================
# 2. ระบบ Web Server จำลอง (สำหรับคงสถานะ Render)
# ==========================================
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"iKALABot Super Full Options is running!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()

# ==========================================
# 3. ฟังก์ชัน AI สำรอง (OpenRouter / Gemma 2 Free)
# ==========================================
def ask_openrouter(text):
    if not OPENROUTER_API_KEY:
        return "❌ ขาด OPENROUTER_API_KEY"
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "google/gemma-2-9b-it:free",
                "messages": [{"role": "user", "content": text}]
            })
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ OpenRouter Error ({response.status_code})"
    except Exception as e:
        logger.error(f"OpenRouter Error: {str(e)}")
        return f"❌ ระบบ OpenRouter ขัดข้อง: {str(e)}"

# ฟังก์ชันดึงวันและเวลาปัจจุบัน พร้อมให้บอทรู้ข่าวสาร
def get_system_context():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[ข้อมูลระบบ: วันเวลาปัจจุบันคือ {now} น. คุณคือ iKALABot ผู้ช่วยอัจฉริยะระดับสูงที่มีความสามารถรอบด้าน]"

# ==========================================
# 4. ระบบ Telegram Bot (Polling + Full Multimodal Functions)
# ==========================================
if not TELEGRAM_BOT_TOKEN:
    logger.error("ERROR: ไม่พบ TELEGRAM_BOT_TOKEN")
else:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "🤖 **iKALABot Super Full Options**\n\n"
            "💬 **พิมพ์ข้อความธรรมดา / URL Link:** สนทนา, ค้นหาข้อมูล, และอ่านเว็บ\n"
            "🎙️ **ส่งข้อความเสียง (Voice):** ถอดรหัสเสียงและตอบกลับทันที\n"
            "📸 **ส่งรูปภาพ (Vision):** วิเคราะห์ภาพถ่ายมัลติโมเดล\n"
            "📁 **ส่งไฟล์ Script / Office / Document:** อ่านไฟล์ ตรวจสอบโค้ด จัดรูปแบบ และเพิ่มคอมเมนต์แจกแจงรายละเอียด\n"
            "🤖 **คำสั่ง /ai หรือ /llama:** เรียกใช้ OpenRouter สำรอง"
        )
        bot.reply_to(message, welcome_text)

    # คำสั่งเรียก OpenRouter สำรอง
    @bot.message_handler(commands=['ai', 'llama'])
    def handle_openrouter_cmd(message):
        text = message.text.replace('/ai', '').replace('/llama', '').strip()
        if not text:
            bot.reply_to(message, "กรุณาพิมพ์ข้อความต่อท้ายด้วยครับ เช่น /ai ขอโค้ดไพธอนหน่อย")
            return
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, f"🤖 **OpenRouter (Gemma 2):**\n{ask_openrouter(text)}")

    # 4.1 โต้ตอบข้อความแชทปกติ & URL Link Reading
    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        text = message.text
        bot.send_chat_action(message.chat.id, 'typing')
        
        # ฟังก์ชันอ่าน URL Link หากพบลิงก์ในข้อความ
        if "http://" in text or "https://" in text:
            try:
                bot.reply_to(message, "🔍 กำลังดึงและอ่านเนื้อหาจาก URL Link...")
                url_extracted = text.split()[0] # ดึงลิงก์คำแรก
                web_res = requests.get(url_extracted, timeout=5)
                soup = BeautifulSoup(web_res.text, 'html.parser')
                web_text = soup.get_text()[:3000]
                text = f"โปรดสรุปและวิเคราะห์เนื้อหาจากลิงก์นี้:\n{web_text}"
            except Exception as e:
                logger.warning(f"URL Read Error: {str(e)}")

        prompt = f"{get_system_context()}\nคำถามจากผู้ใช้: {text}"
        
        if not gemini_client:
            bot.reply_to(message, "⚠️ ไม่พบ Gemini API Key สลับไปใช้ OpenRouter...\n\n" + ask_openrouter(text))
            return
            
        try:
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )
            bot.reply_to(message, response.text)
        except Exception as e:
            logger.error(f"Gemini Error: {str(e)}")
            fallback_msg = f"⚠️ Gemini ขัดข้อง กำลังสลับไปใช้ OpenRouter...\n\n🤖:\n{ask_openrouter(text)}"
            bot.reply_to(message, fallback_msg)

    # 4.2 โต้ตอบข้อความเสียง (Real Audio Speech-to-Text)
    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice(message):
        bot.send_chat_action(message.chat.id, 'record_audio')
        try:
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            temp_audio_path = "temp_voice.ogg"
            with open(temp_audio_path, 'wb') as f:
                f.write(downloaded_file)
            
            bot.reply_to(message, "🎙️ กำลังให้ Gemini ฟังเสียงที่คุณพูด...")
            audio_file_ref = gemini_client.files.upload(file=temp_audio_path)
            
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[
                    audio_file_ref, 
                    f"{get_system_context()}\nช่วยฟังไฟล์เสียงนี้ ถอดความออกมา และตอบคำถามหรือทำตามคำสั่งในเสียงนั้น"
                ]
            )
            
            bot.reply_to(message, f"🗣️ **ผลลัพธ์จากเสียงพูด:**\n\n{response.text}")
            
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        except Exception as e:
            logger.error(f"Voice Error: {str(e)}")
            bot.reply_to(message, f"❌ เกิดข้อผิดพลาดในการประมวลผลเสียง: {str(e)}")

    # 4.3 อ่านรูปภาพ (Vision Multimodal)
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            temp_img_path = "temp_image.jpg"
            with open(temp_img_path, 'wb') as f:
                f.write(downloaded_file)
                
            img_ref = gemini_client.files.upload(file=temp_img_path)
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[img_ref, f"{get_system_context()}\nช่วยวิเคราะห์รูปภาพนี้อย่างละเอียด และอธิบายรายละเอียดต่างๆ ให้เข้าใจง่าย"]
            )
            
            bot.reply_to(message, f"📸 **ผลการวิเคราะห์รูปภาพ:**\n\n{response.text}")
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
        except Exception as e:
            logger.error(f"Photo Error: {str(e)}")
            bot.reply_to(message, f"❌ ไม่สามารถอ่านรูปภาพได้: {str(e)}")

    # 4.4 อ่านไฟล์เอกสาร, ไฟล์ Office, และ Script ทุกนามสกุล (พร้อมจัดบรรทัดโค้ด & เพิ่ม Comment โพสต์แจกแจงรายละเอียด)
    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        file_name = message.document.file_name
        bot.reply_to(message, f"📁 กำลังตรวจสอบและอ่านไฟล์: {file_name}")
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # รองรับไฟล์ script และเอกสารข้อความ
            if file_name.endswith(('.py', '.js', '.txt', '.json', '.html', '.css', '.cpp', '.h', '.sql', '.sh', '.md', '.csv')):
                code_content = downloaded_file.decode('utf-8')[:6000]
                prompt = (
                    f"{get_system_context()}\n"
                    f"นี่คือเนื้อหาจากไฟล์ Script/Document ชื่อ '{file_name}':\n\n{code_content}\n\n"
                    "คำสั่ง: \n"
                    "1. ช่วยตรวจสอบและจัดการปัญหา Code Script (แก้บั๊ก/หาข้อผิดพลาด)\n"
                    "2. จัดบรรทัดโค้ด (Code Formatting) ให้สวยงามอ่านง่าย\n"
                    "3. เพิ่ม Comment โพสต์/อธิบายแจกแจงรายละเอียดการทำงานในแต่ละส่วนของโค้ดให้ครบถ้วนชัดเจน"
                )
                
                response = gemini_client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                bot.reply_to(message, f"🛠️ **ผลการวิเคราะห์ จัดรูปแบบ Script และเพิ่ม Comment:**\n\n{response.text}")
            else:
                # สำหรับไฟล์ Office เช่น .docx, .pdf ฯลฯ ส่งให้ Gemini อ่านผ่าน File API โดยตรง
                temp_doc_path = f"temp_{file_name}"
                with open(temp_doc_path, 'wb') as f:
                    f.write(downloaded_file)
                
                doc_ref = gemini_client.files.upload(file=temp_doc_path)
                response = gemini_client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[doc_ref, f"{get_system_context()}\nช่วยอ่าน สรุปเนื้อหา และแจกแจงรายละเอียดสำคัญจากไฟล์ Office/Document นี้ให้หน่อยครับ"]
                )
                bot.reply_to(message, f"📄 **ผลการอ่านไฟล์ {file_name}:**\n\n{response.text}")
                
                if os.path.exists(temp_doc_path):
                    os.remove(temp_doc_path)
                    
        except Exception as e:
            logger.error(f"Document Error: {str(e)}")
            bot.reply_to(message, f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")

    if __name__ == "__main__":
        threading.Thread(target=run_server, daemon=True).start()
        logger.info("🔄 กำลังล้าง Webhook เก่า และเริ่มกระบวนการ Polling...")
        bot.remove_webhook()
        logger.info("✅ Telegram Bot (Super Full Options) กำลังทำงาน...")
        bot.infinity_polling()
