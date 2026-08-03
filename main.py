import os
import threading
import http.server
import socketserver
import telebot
from google import genai

# ==========================================
# 1. ตั้งค่าพื้นฐาน (ดึงค่าจาก Environment Variables ของ Render)
# ==========================================
PORT = int(os.environ.get("PORT", 8080))
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ==========================================
# 2. ระบบ Web Server จำลอง (ให้ UptimeRobot และ Render เห็นว่าแอปทำงานอยู่)
# ==========================================
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"iKALABot is running and online!")
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
# 3. ระบบ Telegram Bot + AI (Gemini 3.6 Flash)
# ==========================================
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    print("❌ ERROR: ไม่พบ API Key กรุณาตรวจสอบ Environment Variables บน Render")
else:
    # เปิดการเชื่อมต่อ Bot และ AI
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    ai_client = genai.Client(api_key=GEMINI_API_KEY)

    # เมื่อพิมพ์ /start หรือ /help
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = "สวัสดีครับ! ผมคือ iKALABot ขับเคลื่อนด้วย Gemini 3.6 Flash มีอะไรให้ผมช่วยไหมครับ?"
        bot.reply_to(message, welcome_text)

    # เมื่อพิมพ์ข้อความอื่นๆ (ส่งให้ AI ประมวลผล)
    @bot.message_handler(func=lambda message: True)
    def chat_with_ai(message):
        try:
            # แสดงสถานะ "กำลังพิมพ์..." ใน Telegram
            bot.send_chat_action(message.chat.id, 'typing')
            
            # ส่งข้อความไปให้ Gemini 3.6 Flash คิด
            response = ai_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=message.text,
            )
            
            # ส่งคำตอบกลับไปที่แชท
            bot.reply_to(message, response.text)
            
        except Exception as e:
            error_msg = f"ขออภัยครับ เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"
            bot.reply_to(message, error_msg)

    if __name__ == "__main__":
        # รัน Web Server เป็น Background
        threading.Thread(target=run_server, daemon=True).start()
        
        print("✅ Telegram Bot กำลังทำงานและพร้อมรับข้อความ...")
        # รัน Bot เป็น Foreground เพื่อรอรับข้อความ
        bot.infinity_polling()
