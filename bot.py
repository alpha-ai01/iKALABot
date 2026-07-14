import os
from flask import Flask, request
import telebot
from groq import Groq

# ดึงค่าจาก Environment Variables
API_TOKEN = os.environ.get('API_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(API_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
server = Flask(__name__)

# --- ระบบตอบโต้ด้วย AI ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # ใช้โมเดลล่าสุดที่รองรับ
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama-3.3-70b-versatile", 
        )
        response_text = chat_completion.choices[0].message.content
        bot.reply_to(message, response_text)
    except Exception as e:
        bot.reply_to(message, "ขออภัยครับ เกิดข้อผิดพลาด")
        print(f"DEBUG_ERROR: {e}")

# --- ระบบ Webhook (แก้ Error 409) ---
@server.route('/' + API_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/set_webhook")
def set_webhook():
    # เปลี่ยน URL ตรงนี้ให้เป็น URL บอทของคุณบน Render
    bot.remove_webhook()
    bot.set_webhook(url=f"https://ikalabot.onrender.com/{API_TOKEN}")
    return "Webhook set successfully!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
