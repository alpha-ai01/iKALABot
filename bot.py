import os
from flask import Flask, request
import telebot
from groq import Groq

# ดึงค่าจาก Environment Variables (ปลอดภัยและป้องกัน Error)
API_TOKEN = os.environ.get('API_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(API_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
server = Flask(__name__)

# --- ส่วน Logic การคุยกับ AI ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # ใช้ model ใหม่ที่ใช้งานได้จริง
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama-3.1-8b-instant", 
        )
        response_text = chat_completion.choices[0].message.content
        bot.reply_to(message, response_text)
    except Exception as e:
        bot.reply_to(message, "ขออภัยครับ เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI")
        print(f"DEBUG_ERROR: {e}")

# --- ส่วนรับข้อมูลจาก Telegram (Webhook) ---
@server.route('/' + API_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# --- ส่วนตั้งค่า Webhook (ต้องเข้าลิงก์นี้ 1 ครั้งหลังจาก Deploy) ---
@server.route("/set_webhook")
def set_webhook():
    bot.remove_webhook()
    # เปลี่ยน ikalabot.onrender.com เป็น URL ของคุณ
    bot.set_webhook(url=f"https://ikalabot.onrender.com/{API_TOKEN}")
    return "Webhook set successfully!", 200

# --- รัน Server ---
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
