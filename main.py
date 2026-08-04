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

# OpenRouter Client (ตัวสำรอง - โมเดลฟรีตามไกด์ไลน์)
openrouter_client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
) if OPENROUTER_KEY else None

OPENROUTER_FREE_MODEL = "google/gemma-2-9b-it:free"

# ==========================================
# 3. AI Guidelines & System Instruction
# ==========================================
SYSTEM_INSTRUCTION = (
    "คุณคือ iKALABot ผู้ช่วยอัจฉริยะ\n"
    "ข้อกำหนดในการตอบกลับ (Strict Guidelines):\n"
    "1. ตอบกลับด้วยข้อความธรรมดาล้วนเท่านั้น (Plain Text)\n"
    "2. ห้ามใช้สัญลักษณ์ Markdown ทุกชนิด เช่น ห้ามใช้ **ตัวหนา**, *ตัวเอียง*, # หัวข้อ, `โค้ด`, หรือบล็อกข้อความ\n"
    "3. ตอบคำถามอย่างกระชับ ชัดเจน สุภาพ และได้ใจความ"
)

# ==========================================
# 4. ฟังก์ชันประมวลผล AI พร้อมระบบ Fallback
# ==========================================
def get_ai_response(prompt_text):
    # 4.1 ลองใช้ Gemini ตัวหลัก
    if gemini_client:
        try:
            res = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{SYSTEM_INSTRUCTION}\n\nคำถามจากผู้ใช้: {prompt_text}"
            )
            if res and res.text:
                return res.text
        except Exception as e:
            print(f"[Gemini Exception]: {e}")

    # 4.2 สลับมาใช้ OpenRouter โมเดลฟรี
    if openrouter_client:
        try:
            print(f"[Fallback] Switched to OpenRouter Free Model: {OPENROUTER_FREE_MODEL}")
            completion = openrouter_client.chat.completions.create(
                model=OPENROUTER_FREE_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt_text}
                ],
            )
            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content
        except Exception as e:
            print(f"[OpenRouter Exception]: {e}")

    # 4.3 ถ้าล่มทั้งคู่ ตอบแจ้งเตือนแทนการเงียบ
    return "ขออภัยครับ ขณะนี้ระบบ AI ขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้งในภายหลัง"

# ==========================================
# 5. Telegram Message Handlers
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "สวัสดีครับ iKALABot พร้อมทำงานแล้วครับ!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    reply = get_ai_response(message.text)
    bot.reply_to(message, reply)

# ==========================================
# 6. รันระบบ Multi-Threading (ล้าง Webhook ป้องกัน Error 409)
# ==========================================
def run_bot():
    try:
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
