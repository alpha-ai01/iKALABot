import os
import telebot
from flask import Flask, request, abort
from groq import Groq

# ---------------------------------------------------------
# 1. โหลดตั้งค่าและ API Keys
# ---------------------------------------------------------
TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API = os.environ.get('GROQ_API_KEY')
APP_URL = "https://ikalabot.onrender.com"  # หากเปลี่ยนชื่อโปรเจกต์ใน Render ต้องมาเปลี่ยนตรงนี้ด้วย

# ---------------------------------------------------------
# 2. เริ่มต้นระบบ (Initialize)
# ---------------------------------------------------------
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
client = Groq(api_key=GROQ_API)

# ---------------------------------------------------------
# 3. Webhook Endpoint สำหรับรับข้อมูลจาก Telegram
# ---------------------------------------------------------
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    # ตรวจสอบว่าเป็นข้อมูล JSON จาก Telegram จริงๆ
    if request.headers.get('content-type') == 'application/json':
        # ใช้ get_data(as_text=True) ซึ่งเป็นวิธีมาตรฐานและปลอดภัยที่สุดของ Flask
        json_string = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '!', 200
    else:
        abort(403)

# ---------------------------------------------------------
# 4. Route สำหรับ Health Check (ให้ Render ตรวจสอบสถานะ)
# ---------------------------------------------------------
@app.route('/', methods=['GET', 'HEAD'])
def index():
    # ป้องกัน Error ใน Log เวลา Render ยิงมาเช็คว่าเซิร์ฟเวอร์ยังไม่ตาย
    return "Bot is running on Render!", 200

# ---------------------------------------------------------
# 5. ฟังก์ชันหลัก: ประมวลผลข้อความและตอบกลับด้วย AI
# ---------------------------------------------------------
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # แสดงสถานะ "กำลังพิมพ์..." ให้ผู้ใช้เห็นระหว่างรอ AI ประมวลผล
        bot.send_chat_action(message.chat.id, 'typing')
        
        # ส่งข้อความไปให้ Groq (Llama3) ประมวลผล
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama3-8b-8192",
        )
        
        # ดึงข้อความที่ AI ตอบกลับมา
        reply_text = chat_completion.choices[0].message.content
        
        # ส่งกลับไปยัง Telegram
        bot.reply_to(message, reply_text)
        
    except Exception as e:
        # หาก Groq API มีปัญหา หรือมี Error อื่นๆ จะได้แจ้งเตือน
        bot.reply_to(message, "ขออภัยครับ ระบบ AI เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง")
        print(f"AI Error: {e}")

# ---------------------------------------------------------
# 6. คำสั่งเปิดใช้งานเซิร์ฟเวอร์
# ---------------------------------------------------------
if __name__ == "__main__":
    # ล้าง Webhook เก่าที่อาจค้างอยู่ และตั้งค่า Webhook ใหม่ไปที่ Render
    bot.remove_webhook()
    bot.set_webhook(url=f"{APP_URL}/{TOKEN}")
    
    # รัน Flask Server ด้วย Port ที่ Render กำหนด
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
