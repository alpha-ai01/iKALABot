import os
import threading
import http.server
import socketserver
import telebot
import requests
import json

# ==========================================
# 1. ตั้งค่าพื้นฐาน (ดึงค่าจาก Environment Variables)
# ==========================================
PORT = int(os.environ.get("PORT", 8080))
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# ==========================================
# 2. ระบบ Web Server จำลอง
# ==========================================
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"iKALABot is running with OpenRouter!")
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
# 3. ระบบ Telegram Bot + OpenRouter AI
# ==========================================
if not TELEGRAM_BOT_TOKEN or not OPENROUTER_API_KEY:
    print("❌ ERROR: ไม่พบ TELEGRAM_BOT_TOKEN หรือ OPENROUTER_API_KEY")
else:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = "สวัสดีครับ! ผมคือ iKALABot ตอนนี้ผมใช้สมองจาก OpenRouter (Llama 3.1) พิมพ์คำถามมาได้เลยครับ!"
        bot.reply_to(message, welcome_text)

    @bot.message_handler(func=lambda message: True)
    def chat_with_ai(message):
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": "meta-llama/llama-3.1-8b-instruct:free",
                    "messages": [{"role": "user", "content": message.text}]
                })
            )
            
            if response.status_code == 200:
                result = response.json()
                reply_text = result['choices'][0]['message']['content']
                bot.reply_to(message, reply_text)
            else:
                error_msg = f"❌ OpenRouter Error ({response.status_code}): {response.text}"
                bot.reply_to(message, error_msg)
                
        except Exception as e:
            bot.reply_to(message, f"❌ เกิดข้อผิดพลาดของระบบ: {str(e)}")

    if __name__ == "__main__":
        threading.Thread(target=run_server, daemon=True).start()
        
        # --- ลบ Webhook เก่าที่ค้างอยู่ตรงนี้ ---
        print("🔄 กำลังลบ Webhook เก่าที่ค้างอยู่...")
        bot.remove_webhook()
        
        print("✅ Telegram Bot (OpenRouter Mode) กำลังทำงาน...")
        bot.infinity_polling()
