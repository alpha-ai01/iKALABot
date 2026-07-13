import os
import telebot
from groq import Groq
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ==========================================
# 1. ส่วนของเว็บเซิร์ฟเวอร์จำลอง (เพื่อหลอก Render)
# ==========================================
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_dummy_server():
    # Render จะส่งค่า Port มาให้ทาง Environment Variable
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

# สั่งให้เว็บเซิร์ฟเวอร์ทำงานแยกอีกเส้นทาง (Thread) เบื้องหลัง
threading.Thread(target=run_dummy_server, daemon=True).start()


# ==========================================
# 2. ส่วนของบอท Telegram (ทำงานตามปกติ)
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = "สวัสดีครับ! ผมคือ AI Bot ที่ขับเคลื่อนด้วยความเร็วของ Groq พิมพ์ข้อความมาคุยกันได้เลยครับ"
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message.text,
                }
            ],
            model="llama3-8b-8192", 
        )
        reply = chat_completion.choices[0].message.content
        bot.reply_to(message, reply)
        
    except Exception as e:
        bot.reply_to(message, "ขออภัยครับ เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI")
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
