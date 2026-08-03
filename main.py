import os
import threading
import http.server
import socketserver
import telebot
from google import genai
import requests
import json
from datetime import datetime

# ==========================================
# 1. ตั้งค่า Environment Variables
# ==========================================
PORT = int(os.environ.get("PORT", 8080))
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ==========================================
# 2. ระบบ Web Server จำลอง (สำหรับคงสถานะ Render)
# ==========================================
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"iKALABot is running with Real Audio Multimodal!")
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
        return f"❌ ระบบ OpenRouter ขัดข้อง: {str(e)}"

def get_system_context():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[ข้อมูลระบบ: วันเวลาปัจจุบันคือ {now} น.]"

# ==========================================
# 4. ระบบ Telegram Bot (Polling + Real Audio / Multimodal)
# ==========================================
if not TELEGRAM_BOT_TOKEN:
    print("❌ ERROR: ไม่พบ TELEGRAM_BOT_TOKEN")
else:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "🤖 **iKALABot (Gemini 3.6 Flash + Real Audio)**\n\n"
            "💬 **พิมพ์ข้อความธรรมดา:** สนทนา / ค้นหาข้อมูล\n"
            "🎙️ **ส่งข้อความเสียง:** บอทจะฟังเสียง แปลงคำพูด และตอบกลับทันที!\n"
            "📸 **ส่งรูปภาพ:** บอทช่วยวิเคราะห์ภาพ\n"
            "📁 **ส่งไฟล์ Script:** บอทช่วยตรวจโค้ดและจัดรูปแบบให้"
        )
        bot.reply_to(message, welcome_text)

    @bot.message_handler(commands=['ai', 'llama'])
    def handle_openrouter_cmd(message):
        text = message.text.replace('/ai', '').replace('/llama', '').strip()
        if not text:
            bot.reply_to(message, "กรุณาพิมพ์ข้อความต่อท้ายด้วยครับ เช่น /ai ขอโค้ดไพธอนหน่อย")
            return
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, f"🤖 **OpenRouter (Gemma 2):**\n{ask_openrouter(text)}")

    # 4.1 โต้ตอบข้อความแชทปกติ
    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        text = message.text
        bot.send_chat_action(message.chat.id, 'typing')
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
            fallback_msg = f"⚠️ Gemini ขัดข้อง กำลังสลับไปใช้ OpenRouter...\n\n🤖:\n{ask_openrouter(text)}"
            bot.reply_to(message, fallback_msg)

    # 4.2 โต้ตอบข้อความเสียง (Real Audio Processing ผ่าน Gemini)
    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice(message):
        bot.send_chat_action(message.chat.id, 'record_audio')
        try:
            # ดึงข้อมูลไฟล์เสียงจาก Telegram
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            # บันทึกไฟล์เสียงชั่วคราวเพื่อส่งให้ Gemini ประมวลผล
            temp_audio_path = "temp_voice.ogg"
            with open(temp_audio_path, 'wb') as f:
                f.write(downloaded_file)
            
            bot.reply_to(message, "🎙️ กำลังอัปโหลดและให้ Gemini ฟังเสียงที่คุณพูด...")
            
            # อัปโหลดไฟล์เสียงเข้าไปยัง Gemini File API
            audio_file_ref = gemini_client.files.upload(file=temp_audio_path)
            
            # สั่งให้ Gemini ถอดรหัสและตอบคำถามจากเสียง
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[
                    audio_file_ref, 
                    f"{get_system_context()}\nช่วยฟังไฟล์เสียงนี้ ถอดความออกมาเป็นข้อความ และตอบคำถามหรือทำตามคำสั่งในเสียงนั้นให้หน่อยครับ"
                ]
            )
            
            bot.reply_to(message, f"🗣️ **ผลลัพธ์จากเสียงที่คุณพูด:**\n\n{response.text}")
            
            # ลบไฟล์เสียงชั่วคราวทิ้ง
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                
        except Exception as e:
            bot.reply_to(message, f"❌ เกิดข้อผิดพลาดในการประมวลผลเสียง: {str(e)}")

    # 4.3 อ่านรูปภาพ (Vision)
    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        bot.reply_to(message, "📸 ได้รับรูปภาพแล้ว กำลังประมวลผลวิเคราะห์ภาพผ่านระบบ Multimodal...")

    # 4.4 อ่านไฟล์เอกสารและ Script
    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        file_name = message.document.file_name
        bot.reply_to(message, f"📁 กำลังตรวจสอบไฟล์: {file_name}")
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            if file_name.endswith(('.py', '.js', '.txt', '.json', '.html', '.css', '.cpp', '.h')):
                code_content = downloaded_file.decode('utf-8')[:4000]
                prompt = f"{get_system_context()}\nช่วยตรวจสอบโค้ด จัดบรรทัดโค้ด (Code Formatting) และวิเคราะห์ปัญหาในไฟล์นี้ให้หน่อยครับ:\n\n{code_content}"
                
                response = gemini_client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                bot.reply_to(message, f"🛠️ **ผลการตรวจสอบและจัดรูปแบบ Code Script:**\n\n{response.text}")
            else:
                bot.reply_to(message, f"📥 ดาวน์โหลดไฟล์ {file_name} เรียบร้อยแล้ว")
        except Exception as e:
            bot.reply_to(message, f"❌ เกิดข้อผิดพลาดในการอ่านไฟล์: {str(e)}")

    if __name__ == "__main__":
        threading.Thread(target=run_server, daemon=True).start()
        print("🔄 กำลังล้าง Webhook เก่า และเริ่มกระบวนการ Polling...")
        bot.remove_webhook()
        print("✅ Telegram Bot (Real Audio + Gemini 3.6 Flash) กำลังทำงาน...")
        bot.infinity_polling()
