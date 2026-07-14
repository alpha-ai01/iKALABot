import os
import telebot
from flask import Flask, request, abort
from groq import Groq

# 1. ดึงข้อมูลจาก Environment ของ Render
TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API = os.environ.get('GROQ_API_KEY')
APP_URL = "https://ikalabot.onrender.com"  # URL ของคุณบน Render

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ตรวจสอบเบื้องต้นว่ามี API Key อยู่ในระบบไหม
if not GROQ_API:
    print("❌ ไม่พบ GROQ_API_KEY ในระบบ Environment Variables!")
else:
    print("🔑 ตรวจพบ GROQ_API_KEY ในระบบแล้ว")

# เริ่มต้นระบบ Groq
try:
    client = Groq(api_key=GROQ_API)
except Exception as e:
    print(f"❌ ไม่สามารถโหลด Groq Client ได้: {e}")
    client = None

# 2. Webhook Endpoint
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        # ใช้ get_data วิธีมาตรฐาน ปลอดภัย ไม่พังแน่นอน
        json_string = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '!', 200
    else:
        abort(403)

# 3. หน้าบ้านสำหรับให้ Render เช็คสถานะ (Health Check)
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return "Bot is running perfectly on Render!", 200

# 4. ฟังก์ชันจัดการเมื่อได้รับข้อความ
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(f"📩 ได้รับข้อความ: {message.text}")
    
    if not GROQ_API or not client:
        bot.reply_to(message, "❌ AI ไม่พร้อมใช้งานเนื่องจากไม่ได้ตั้งค่า GROQ_API_KEY")
        return

    try:
        # แสดงสถานะ "กำลังพิมพ์..."
        bot.send_chat_action(message.chat.id, 'typing')
        
        # ส่งข้อความไปให้ Groq AI
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama3-8b-8192",
        )
        
        # ส่งคำตอบกลับไปหาผู้ใช้
        reply_text = chat_completion.choices[0].message.content
        bot.reply_to(message, reply_text)
        print("📤 ตอบกลับด้วย AI สำเร็จ")
        
    except Exception as e:
        # พ่น Error จริงๆ ออกมาในแชทให้เห็นเลยว่า AI พังเพราะอะไร!
        print(f"❌ AI Error: {e}")
        bot.reply_to(message, f"⚠️ AI เกิดข้อผิดพลาด:\n`{str(e)}`", parse_mode="Markdown")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
