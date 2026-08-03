import os
import threading
import http.server
import socketserver
import telebot
from google import genai
import requests
import json

# ==========================================
# 1. ดึงค่าตัวแปร (Environment Variables)
# ==========================================
PORT = int(os.environ.get("PORT", 8080))
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ==========================================
# 2. ระบบ Web Server (ป้องกัน Render ปิดแอป)
# ==========================================
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"iKALABot Dual AI is running!")
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
# 3. ฟังก์ชันสำหรับยิง API ไปหา OpenRouter
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
                "model": "meta-llama/llama-3.1-8b-instruct",
                "messages": [{"role": "user", "content": text}]
            })
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ OpenRouter Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"❌ ระบบ OpenRouter ขัดข้อง: {str(e)}"

# ==========================================
# 4. ระบบ Telegram Bot
# ==========================================
if not TELEGRAM_BOT_TOKEN:
    print("❌ ERROR: ไม่พบ TELEGRAM_BOT_TOKEN")
else:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "สวัสดีครับ! ผมคือ iKALABot (Dual AI)\n\n"
            "💬 พิมพ์ข้อความปกติ = ใช้ **Gemini 3.6 Flash**\n"
            "🦙 พิมพ์ /llama <ข้อความ> = ใช้ **Llama 3.1**"
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown")

    # บังคับใช้ OpenRouter
    @bot.message_handler(commands=['llama'])
    def handle_llama(message):
        text = message.text.replace('/llama', '').strip()
        if not text:
            bot.reply_to(message, "กรุณาพิมพ์คำถามต่อท้าย /llama ด้วยครับ เช่น `/llama สวัสดี`", parse_mode="Markdown")
            return
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, f"🦙 **Llama 3.1:**\n{ask_openrouter(text)}", parse_mode="Markdown")

    # ค่าเริ่มต้นใช้ Gemini (มี Fallback ไป OpenRouter)
    @bot.message_handler(func=lambda message: True)
    def chat_with_gemini(message):
        bot.send_chat_action(message.chat.id, 'typing')
        if not gemini_client:
            bot.reply_to(message, "⚠️ ไม่พบ Gemini API Key สลับไปใช้ OpenRouter แทน...\n\n" + ask_openrouter(message.text))
            return
            
        try:
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=message.text,
            )
            bot.reply_to(message, f"✨ **Gemini:**\n{response.text}", parse_mode="Markdown")
        except Exception as e:
            fallback_msg = f"⚠️ Gemini ขัดข้อง ({str(e)})\nกำลังสลับไปใช้ OpenRouter แทน...\n\n🦙 **Llama 3.1:**\n{ask_openrouter(message.text)}"
            bot.reply_to(message, fallback_msg, parse_mode="Markdown")

    if __name__ == "__main__":
        threading.Thread(target=run_server, daemon=True).start()
        
        print("🔄 กำลังล้าง Webhook เก่า...")
        bot.remove_webhook()
        
        print("✅ Telegram Bot (Dual AI Mode) กำลังทำงาน...")
        bot.infinity_polling()
