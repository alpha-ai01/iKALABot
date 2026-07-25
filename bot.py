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
from openrouter import OpenRouter
from gtts import gTTS

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") # รองรับตัวแปร OpenRouter API Key[span_0](start_span)[span_0](end_span)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# กำหนดค่า Client สำหรับ Gemini และ OpenRouter
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
openrouter_client = OpenRouter(api_key=OPENROUTER_API_KEY) if OPENROUTER_API_KEY else None

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "iKALABot Voice Edition with OpenRouter is running and alive!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

def self_ping_service():
    time.sleep(10)
    target_url = RENDER_EXTERNAL_URL if RENDER_EXTERNAL_URL else "http://localhost:10000/"
    
    while True:
        try:
            response = requests.get(target_url)
            logging.info(f"Self-Ping sent to {target_url} - Status: {response.status_code}")
        except Exception as e:
            logging.error(f"Self-Ping failed: {e}")
        
        time.sleep(300)

user_interaction_ids = {}

def clean_text_for_telegram(text: str) -> str:
    if "```" in text:
        parts = text.split("```")
        cleaned_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 0:
                cleaned_parts.append(re.sub(r'\*+', '', part))
            else:
                cleaned_parts.append(part)
        return "```".join(cleaned_parts)
    else:
        return re.sub(r'\*+', '', text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "สวัสดีครับ! ผมคือ iKALABot (รองรับ Multi-Model และเสียง 🎙️) 🤖\n"
        "ยินดีให้บริการครับ คุณสามารถส่งข้อความ รูปภาพ หรือกดอัดเสียงคุยกับผมได้เลย!\n"
        "(พิมพ์ /clear เพื่อเริ่มคุยเรื่องใหม่)"
    )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_interaction_ids:
        del user_interaction_ids[user_id]
    await update.message.reply_text("ล้างประวัติการสนทนาเรียบร้อยแล้วครับ! 🧹")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="record_voice")
    
    temp_file_path = None
    reply_audio_path = None
    
    try:
        prev_id = user_interaction_ids.get(user_id)
        is_voice_message = False

        if update.message.voice:
            is_voice_message = True
            voice_file = await update.message.voice.get_file()
            temp_file_path = f"voice_{user_id}.ogg"
            await voice_file.download_to_drive(temp_file_path)
            
            uploaded_file = client.files.upload(file=temp_file_path)
            input_data = [
                {"type": "text", "text": "ถอดความและตอบกลับข้อความเสียงนี้เป็นภาษาไทย"},
                {
                    "type": "audio",
                    "uri": uploaded_file.uri,
                    "mime_type": uploaded_file.mime_type
                }
            ]

        elif update.message.photo:
            caption = update.message.caption or "อธิบายรูปภาพนี้ให้ฟังหน่อย"
            photo_file = await update.message.photo[-1].get_file()
            temp_file_path = f"photo_{user_id}.jpg"
            await photo_file.download_to_drive(temp_file_path)
            
            uploaded_file = client.files.upload(file=temp_file_path)
            input_data = [
                {"type": "text", "text": caption},
                {
                    "type": "image",
                    "uri": uploaded_file.uri,
                    "mime_type": uploaded_file.mime_type
                }
            ]
        else:
            input_data = update.message.text

        # ตัวอย่างการเลือกใช้งานโมเดล (สามารถเลือกใช้ Gemini หรือสลับมาใช้ OpenRouter ตามต้องการได้ที่นี่)
        kwargs = {
            "model": "gemini-3.6-flash",
            "input": input_data
        }
        
        if prev_id:
            kwargs["previous_interaction_id"] = prev_id

        interaction = client.interactions.create(**kwargs)
        user_interaction_ids[user_id] = interaction.id
        
        raw_reply = interaction.output_text if interaction.output_text else "ขออภัย ไม่สามารถประมวลผลคำตอบได้"
        reply_text = clean_text_for_telegram(raw_reply)
        
        await update.message.reply_text(reply_text)

        if is_voice_message:
            reply_audio_path = f"reply_{user_id}.mp3"
            tts = gTTS(text=reply_text, lang='th')
            tts.save(reply_audio_path)
            
            with open(reply_audio_path, 'rb') as audio:
                await update.message.reply_voice(voice=audio)

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้งครับ")
        
    finally:
        for path in [temp_file_path, reply_audio_path]:
            if path and os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("ERROR: Missing TELEGRAM_BOT_TOKEN or GEMINI_API_KEY")
    else:
        t_server = threading.Thread(target=run_server)
        t_server.daemon = True
        t_server.start()
        
        t_ping = threading.Thread(target=self_ping_service)
        t_ping.daemon = True
        t_ping.start()
        
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("clear", clear_chat))
        app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.VOICE) & ~filters.COMMAND, handle_message))
        
        print("iKALABot Voice Edition with OpenRouter & Self-Ping is running...")
        app.run_polling()
