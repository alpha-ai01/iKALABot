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

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "iKALABot Voice & Multi-Model Edition is running!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

def self_ping_service():
    time.sleep(10)
    target_url = RENDER_EXTERNAL_URL if RENDER_EXTERNAL_URL else "http://localhost:10000/"
    while True:
        try:
            requests.get(target_url)
        except Exception:
            pass
        time.sleep(300)

def clean_text(text: str) -> str:
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
        "คุณสามารถส่งข้อความ รูปภาพ หรือกดส่งข้อความเสียงมาคุยกับผมได้เลยครับ (บอทจะส่งเสียงตอบกลับให้ทุกข้อความครับ)"
    )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ล้างประวัติการสนทนาเรียบร้อยแล้วครับ! 🧹")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")
    
    temp_file_path = None
    reply_audio_path = None
    
    try:
        input_text = ""
        
        if update.message.voice:
            file = await update.message.voice.get_file()
            temp_file_path = f"voice_{user_id}.ogg"
            await file.download_to_drive(temp_file_path)
            
            if client:
                uploaded = client.files.upload(file=temp_file_path)
                res = client.interactions.create(
                    model="gemini-3.6-flash",
                    input=[
                        {"type": "text", "text": "ถอดความข้อความเสียงนี้เป็นภาษาไทย"},
                        {"type": "audio", "uri": uploaded.uri, "mime_type": uploaded.mime_type}
                    ]
                )
                input_text = res.output_text if res.output_text else "สวัสดีครับ"
            else:
                input_text = "สวัสดีครับ"

        elif update.message.photo:
            caption = update.message.caption or "ช่วยอธิบายรูปภาพนี้ให้ฟังหน่อยครับ"
            file = await update.message.photo[-1].get_file()
            temp_file_path = f"photo_{user_id}.jpg"
            await file.download_to_drive(temp_file_path)
            
            if client:
                uploaded = client.files.upload(file=temp_file_path)
                res = client.interactions.create(
                    model="gemini-3.6-flash",
                    input=[
                        {"type": "text", "text": caption},
                        {"type": "image", "uri": uploaded.uri, "mime_type": uploaded.mime_type}
                    ]
                )
                input_text = res.output_text if res.output_text else caption
            else:
                input_text = caption
        else:
            input_text = update.message.text

        raw_reply = ""
        if OPENROUTER_API_KEY:
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
                        "messages": [{"role": "user", "content": input_text}]
                    },
                    timeout=30
                )
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    raw_reply = data["choices"][0]["message"]["content"]
            except Exception as e:
                logging.error(f"OpenRouter error: {e}")

        if not raw_reply and client:
            res = client.interactions.create(model="gemini-3.6-flash", input=input_text)
            raw_reply = res.output_text if res.output_text else "ขออภัยครับ ไม่สามารถประมวลผลได้ในขณะนี้"

        reply_text = clean_text(raw_reply or "เกิดข้อผิดพลาดในการประมวลผล")
        
        # ส่งข้อความตัวหนังสือตอบกลับ
        await update.message.reply_text(reply_text)

        # ส่งไฟล์เสียง (Voice Note) ตามไปทุกครั้ง เพื่อให้กดฟังแทนการอ่านได้ทันที
        reply_audio_path = f"reply_{user_id}.mp3"
        tts = gTTS(text=reply_text, lang='th')
        tts.save(reply_audio_path)
        with open(reply_audio_path, 'rb') as audio:
            await update.message.reply_voice(voice=audio)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้งครับ")
        
    finally:
        for path in [temp_file_path, reply_audio_path]:
            if path and os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("ERROR: Missing tokens")
    else:
        threading.Thread(target=run_server, daemon=True).start()
        threading.Thread(target=self_ping_service, daemon=True).start()
        
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("clear", clear_chat))
        app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.VOICE) & ~filters.COMMAND, handle_message))
        
        app.run_polling()
