import os
import threading
from flask import Flask
import telebot
from google import genai
import openai

# ==========================================
# 1. ตั้งค่า Flask Server (สำหรับ Render Health Check)
# ==========================================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "iKALABot is running live!", 200

# ==========================================
# 2. ตั้งค่า Telegram & AI Clients
# ==========================================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# Gemini Client (ตัวหลัก)
gemini_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

# OpenRouter Client (ตัวสำรอง - ใช้โมเดลฟรี)
openrouter_client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
) if OPENROUTER_KEY else None

OPENROUTER_FREE_MODEL = "google/gemma-2-9b-it:free"

# ==========================================
# 3. ฟังก์ชันประมวลผล AI
# ==========================================
def get_ai_response(prompt_text):
    # 3.1 เรียกใช้ Gemini ตัวหลัก
    if gemini_client:
        try:
            res = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_text
            )
            if res and res.text:
                return res.text
        except Exception as e:
            print(f"[Gemini Exception]: {e}")

    # 3.2 สลับมาใช้ OpenRouter โมเดลฟรี
    if openrouter_client:
        try:
            print(f"[Fallback] Switched to OpenRouter Free Model: {OPENROUTER_FREE_MODEL}")
            completion = openrouter_client.chat.completions.create(
                model=OPENROUTER_FREE_MODEL,
                messages=[{"role": "user", "content": prompt_text}],
            )
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content
        except Exception as e:
            print(f"[OpenRouter Exception]: {e}")

    # 3.3 ถ้าล่มทั้งคู่ ตอบแจ้งเตือนผู้ใช้แทนการเงียบ
    return "ขออภัยครับ ขณะนี้ระบบ AI ขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้งในภายหลัง"

# ==========================================
# 4. Telegram Message Handlers
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "สวัสดีครับ iKALABot พร้อมทำงานแล้วครับ!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    reply = get_ai_response(message.text)
    bot.reply_to(message, reply)

# ==========================================
# 5. รันระบบแบบ Multi-Threading (ป้องกัน Error 409)
# ==========================================
def run_bot():
    try:
        # ลบ Webhook ค้างเก่าออก ป้องกัน 409 Conflict
        print("Clearing old webhooks...")
        bot.remove_webhook()
        print("Starting Telegram Bot Polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
    except Exception as e:
        print(f"[Polling Error]: {e}")

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
