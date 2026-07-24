import os
import logging
import threading
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ตั้งค่า Logging และปิด Log ระดับ INFO ของ httpx เพื่อป้องกัน Token หลุด
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "iKALABot is running!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

user_interaction_ids = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("สวัสดีครับ! ผมคือ iKALABot 🤖\nยินดีให้บริการครับ พิมพ์คุยกับผมได้เลย\n(พิมพ์ /clear เพื่อเริ่มคุยเรื่องใหม่)")

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_interaction_ids:
        del user_interaction_ids[user_id]
    await update.message.reply_text("ล้างประวัติการสนทนาเรียบร้อยแล้วครับ! 🧹")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        prev_id = user_interaction_ids.get(user_id)
        kwargs = {
            "model": "gemini-3.6-flash",
            "input": user_text
        }
        if prev_id:
            kwargs["previous_interaction_id"] = prev_id

        interaction = client.interactions.create(**kwargs)
        user_interaction_ids[user_id] = interaction.id
        
        reply_text = interaction.output_text if interaction.output_text else "ขออภัย ไม่สามารถประมวลผลคำตอบได้"
        await update.message.reply_text(reply_text)
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง หรือพิมพ์ /clear เพื่อเริ่มใหม่ครับ")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("ERROR: Missing TELEGRAM_BOT_TOKEN or GEMINI_API_KEY")
    else:
        t = threading.Thread(target=run_server)
        t.daemon = True
        t.start()
        
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("clear", clear_chat))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("iKALABot and Web Server running...")
        app.run_polling()
