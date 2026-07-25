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
        is_voice_message = False

        if update.message.voice:
            is_voice_message = True
            voice_file = await update.message.voice.get_file()
            temp_file_path = f"voice_{user_id}.ogg"
            await voice_file.download_to_drive(temp_file_path)
            
            uploaded_file = client.files.upload(file=temp_file_path)
            input_text = "ถอดความและตอบกลับข้อความเสียงนี้เป็นภาษาไทย"
            # จัดการเคสเสียงผ่าน Gemini หลักตามเดิม
        elif update.message.photo:
            caption = update.message.caption or "อธิบายรูปภาพนี้ให้ฟังหน่อย"
            input_text = caption
        else:
            input_text = update.message.text

        # ตัวอย่างการเรียกใช้งาน OpenRouter (ถ้ามีการตั้งค่า API Key ไว้) หรือ fallback ไปใช้ Gemini
        raw_reply = ""
        if OPENROUTER_API_KEY:
            try:
                response = requests.post(
                    url="[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "HTTP-Referer": RENDER_EXTERNAL_URL if RENDER_EXTERNAL_URL else "[https://ikalabot.onrender.com](https://ikalabot.onrender.com)",
                        "X-OpenRouter-Title": "iKALABot",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [{"role": "user", "content": input_text}]
                    },
                    timeout=30
                )
                res_data = response.json()
                if "choices" in res_data and len(res_data["choices"]) > 0:
                    raw_reply = res_data["choices"][0]["message"]["content"]
            except Exception as e:
                logging.error(f"OpenRouter error: {e}")

        # ถ้าไม่ได้เปิดใช้งาน OpenRouter หรือเรียกไม่สำเร็จ ให้ใช้ Gemini เป็นระบบหลักตามเดิม
        if not raw_reply and client:
            kwargs = {
                "model": "gemini-3.6-flash",
                "input": input_text
            }
            prev_id = user_interaction_ids.get(user_id)
            if prev_id:
                kwargs["previous_interaction_id"] = prev_id

            interaction = client.interactions.create(**kwargs)
            user_interaction_ids[user_id] = interaction.id
            raw_reply = interaction.output_text if interaction.output_text else "ขออภัย ไม่สามารถประมวลผลคำตอบได้"

        reply_text = clean_text_for_telegram(raw_reply if raw_reply else "ขออภัย เกิดข้อผิดพลาดในการประมวลผล")
        
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
