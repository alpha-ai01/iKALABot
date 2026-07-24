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

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "iKALABot 2026 Vision Edition is running!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

user_interaction_ids = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "สวัสดีครับ! ผมคือ iKALABot (เวอร์ชัน 2026 รองรับรูปภาพ) 🤖📸\n"
        "ยินดีให้บริการครับ พิมพ์คุย หรือส่งรูปภาพมาให้ผมช่วยดูได้เลย!\n"
        "(พิมพ์ /clear เพื่อเริ่มคุยเรื่องใหม่)"
    )

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_interaction_ids:
        del user_interaction_ids[user_id]
    await update.message.reply_text("ล้างประวัติการสนทนาเรียบร้อยแล้วครับ! 🧹")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    temp_photo_path = None
    try:
        prev_id = user_interaction_ids.get(user_id)
        
        # กรณีผู้ใช้ส่ง "รูปภาพ" มา
        if update.message.photo:
            caption = update.message.caption or "อธิบายรูปภาพนี้ให้ฟังหน่อย"
            photo_file = await update.message.photo[-1].get_file()
            temp_photo_path = f"temp_{user_id}.jpg"
            await photo_file.download_to_drive(temp_photo_path)
            
            # อัปโหลดรูปขึ้น Gemini Files API
            uploaded_file = client.files.upload(file=temp_photo_path)
            
            input_data = [
                {"type": "text", "text": caption},
                {
                    "type": "image",
                    "uri": uploaded_file.uri,
                    "mime_type": uploaded_file.mime_type
                }
            ]
        # กรณีผู้ใช้ส่ง "ข้อความ" ปกติ
        else:
            input_data = update.message.text

        kwargs = {
            "model": "gemini-3.6-flash",
            "input": input_data
        }
        
        if prev_id:
            kwargs["previous_interaction_id"] = prev_id

        interaction = client.interactions.create(**kwargs)
        user_interaction_ids[user_id] = interaction.id
        
        reply_text = interaction.output_text if interaction.output_text else "ขออภัย ไม่สามารถประมวลผลคำตอบได้"
        await update.message.reply_text(reply_text)

    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง หรือพิมพ์ /clear ครับ")
        
    finally:
        # ลบไฟล์รูปภาพชั่วคราวออกจากเซิร์ฟเวอร์เพื่อประหยัดพื้นที่
        if temp_photo_path and os.path.exists(temp_photo_path):
            os.remove(temp_photo_path)

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
        # ดักจับทั้งข้อความตัวอักษร และรูปภาพ
        app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_message))
        
        print("iKALABot 2026 is running...")
        app.run_polling()
