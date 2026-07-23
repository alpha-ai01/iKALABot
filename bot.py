import os
import logging
import threading
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "iKALABot is running!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

user_chats = {}

def get_chat_session(user_id):
    if user_id not in user_chats:
        user_chats[user_id] = model.start_chat(history=[])
    return user_chats[user_id]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "สวัสดีครับ! ผมคือ iKALABot 🤖\nยินดีให้บริการครับ พิมพ์คุยกับผมได้เลย\n(พิมพ์ /clear เพื่อเริ่มคุยเรื่องใหม่)"
    )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_chats:
        del user_chats[user_id]
    await update.message.reply_text("ล้างประวัติการสนทนาเรียบร้อยแล้วครับ! 🧹")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.effective_user.id
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        chat_session = get_chat_session(user_id)
        response = chat_session.send_message(user_text)
        reply_text = response.text if response.text else "ขออภัย ไม่สามารถประมวลผลคำตอบได้"
        await update.message.reply_text(reply_text)
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง หรือพิมพ์ /clear เพื่อล้างความจำครับ")

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
