import os
import logging
import threading
import time
import requests
import re
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from gtts import gTTS

# โหลดตัวแปรสภาพแวดล้อมจากไฟล์ .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

# ตั้งค่า Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# กำหนดค่า Client สำหรับ Gemini API
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

user_histories = {}
MAX_HISTORY_LENGTH = 6

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "iKALABot Secure Free-Tier Edition is running!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

def self_ping_service():
    time.sleep(10)
    target_url = RENDER_EXTERNAL_URL if RENDER_EXTERNAL_URL else "http://localhost:10000/"
    while True:
        try:
            requests.get(target_url, timeout=10)
        except Exception:
            pass
        time.sleep(300)

def clean_text(text: str) -> str:
    if not text:
        return ""
    if "```" in text:
        parts = text.split("```")
        cleaned = []
        for i, p in enumerate(parts):
            if i % 2 == 0:
                cleaned.append(re.sub(r'\*+', '', p))
            else:
                cleaned.append(p)
        return "```".join(cleaned)
    return re.sub(r'\*+', '', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "สวัสดีครับ! iKALABot พร้อมให้บริการแล้วครับ 🤖\n"
        "ระบบรองรับข้อความ รูปภาพ และเสียง พร้อมส่งเสียงตอบกลับอัตโนมัติทุกข้อความครับ"
    )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_histories:
        user_histories[user_id].clear()
    await update.message.reply_text("ล้างประวัติการสนทนาเรียบร้อยแล้วครับ! 🧹")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")
    
    temp_file_path = None
    reply_audio_path = None
    uploaded_file = None
    
    try:
        input_text = ""
        
        # 1. จัดการไฟล์เสียง
        if update.message.voice:
            file = await update.message.voice.get_file()
            temp_file_path = f"voice_{user_id}_{int(time.time())}.ogg"
            await file.download_to_drive(temp_file_path)
            input_text = "ช่วยตอบคำถามจากไฟล์เสียงนี้ให้หน่อยครับ"
            
        # 2. จัดการไฟล์รูปภาพ
        elif update.message.photo:
            photo_file = await update.message.photo[-1].get_file()
            temp_file_path = f"photo_{user_id}_{int(time.time())}.jpg"
            await photo_file.download_to_drive(temp_file_path)
            
            if client:
                try:
                    uploaded_file = client.files.upload(file=temp_file_path)
                except Exception as e:
                    logging.error(f"File upload error encountered: {e}")
            input_text = update.message.caption or "ช่วยอธิบายรูปภาพนี้ให้หน่อยครับ"
            
        # 3. จัดการข้อความ
        else:
            input_text = update.message.text or ""

        if not input_text:
            return

        # บันทึกประวัติการสนทนา
        if user_id not in user_histories:
            user_histories[user_id] = []
        
        history = user_histories[user_id]
        history.append(f"User: {input_text}")
        
        if len(history) > MAX_HISTORY_LENGTH:
            user_histories[user_id] = history[-MAX_HISTORY_LENGTH:]

        context_prompt = "\n".join(user_histories[user_id])
        raw_reply = ""
        
        # ประมวลผลด้วย Gemini API
        if client:
            try:
                if uploaded_file:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[uploaded_file, context_prompt]
                    )
                    raw_reply = response.text if response.text else ""
                else:
                    interaction = client.interactions.create(
                        model="gemini-3.6-flash",
                        input=context_prompt
                    )
                    raw_reply = interaction.output_text if interaction.output_text else ""
            except Exception as e:
                logging.error(f"Gemini primary model error encountered: {e}")

        # ระบบ Fallback ไปยัง OpenRouter
        if not raw_reply and OPENROUTER_API_KEY:
            try:
                response = requests.post(
                    url="[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "HTTP-Referer": RENDER_EXTERNAL_URL or "[https://ikalabot.onrender.com](https://ikalabot.onrender.com)",
                        "X-OpenRouter-Title": "iKALABot",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [{"role": "user", "content": context_prompt}]
                    },
                    timeout=30
                )
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    raw_reply = data["choices"][0]["message"]["content"]
            except Exception as e:
                logging.error(f"OpenRouter fallback error encountered: {e}")

        reply_text = clean_text(raw_reply or "ขออภัยครับ ระบบกำลังหนาแน่น กรุณาลองใหม่อีกครั้งในครู่ครับ")
        user_histories[user_id].append(f"Bot: {reply_text}")

        # ส่งข้อความตอบกลับ
        await update.message.reply_text(reply_text)

        # สร้างเสียง TTS และส่งกลับ
        reply_audio_path = f"reply_{user_id}_{int(time.time())}.mp3"
        tts = gTTS(text=reply_text, lang='th')
        tts.save(reply_audio_path)
        
        with open(reply_audio_path, 'rb') as audio:
            await update.message.reply_voice(voice=audio)

    except Exception as e:
        logging.error(f"Critical error in message handler: {e}")
        await update.message.reply_text("เกิดข้อผิดพลาดขึ้นชั่วคราว ระบบได้ทำการป้องกันความปลอดภัยเรียบร้อยแล้วครับ")
        
    finally:
        for path in [temp_file_path, reply_audio_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
        
        if uploaded_file and client:
            try:
                client.files.delete(name=uploaded_file.name)
            except Exception as e:
                logging.error(f"Failed to delete file from Gemini: {e}")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        print("ERROR: Missing TELEGRAM_TOKEN in environment variables.")
    else:
        threading.Thread(target=run_server, daemon=True).start()
        threading.Thread(target=self_ping_service, daemon=True).start()
        
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("clear", clear_chat))
        app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.VOICE) & ~filters.COMMAND, handle_message))
        
        app.run_polling()
