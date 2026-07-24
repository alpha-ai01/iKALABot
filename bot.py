import os
import logging
import threading
from flask import Flask
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai
from gtts import gTTS

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "iKALABot Voice Edition is running!"

def run_server():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

user_interaction_ids = {}

SYSTEM_INSTRUCTION = (
    "ตอบเข้าประเด็นโดยตรง เอาเฉพาะเนื้อหาเพียวๆ ไม่ต้องกล่าวทักทาย ไม่ต้องเกริ่นนำ "
    "ไม่ต้องใส่คำอธิบายเพิ่มเติม และไม่ต้องมีคำลงท้ายหรือคำพูดสุภาพส่วนเกิน"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "สวัสดีครับ! ผมคือ iKALABot (รองรับการสนทนาด้วยเสียง 🎙️) 🤖\n"
        "ยินดีให้บริการครับ คุณสามารถส่งข้อความ รูปภาพ เอกสาร หรือกดอัดเสียงคุยกับผมได้เลย!\n"
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

        elif update.message.document:
            doc = update.message.document
            caption = update.message.caption or "อ่านและสรุปหรือวิเคราะห์เนื้อหาในไฟล์นี้"
            temp_file_path = f"doc_{user_id}_{doc.file_name}"
            
            doc_file = await doc.get_file()
            await doc_file.download_to_drive(temp_file_path)
            
            uploaded_file = client.files.upload(file=temp_file_path)
            mime_type = uploaded_file.mime_type or doc.mime_type or "application/octet-stream"
            
            input_data = [
                {"type": "text", "text": caption},
                {
                    "type": "document",
                    "uri": uploaded_file.uri,
                    "mime_type": mime_type
                }
            ]

        else:
            input_data = update.message.text

        kwargs = {
            "model": "gemini-2.5-flash",
            "input": input_data,
            "system_instruction": SYSTEM_INSTRUCTION
        }
        
        if prev_id:
            kwargs["previous_interaction_id"] = prev_id

        interaction = client.interactions.create(**kwargs)
        user_interaction_ids[user_id] = interaction.id
        
        reply_text = interaction.output_text if interaction.output_text else "ขออภัย ไม่สามารถประมวลผลคำตอบได้"
        
        await update.message.reply_text(reply_text)

        if is_voice_message:
            reply_audio_path = f"reply_{user_id}.mp3"
            tts = gTTS(text=reply_text, lang='th')
            tts.save(reply_audio_path)
            
            with open(reply_audio_path, 'rb') as audio:
                await update.message.reply_voice(voice=audio)

    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        await update.message.reply_text("เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้งครับ")
        
    finally:
        for path in [temp_file_path, reply_audio_path]:
            if path and os.path.exists(path):
                os.remove(path)

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
        app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.ATTACHMENT | filters.VOICE) & ~filters.COMMAND, handle_message))
        
        print("iKALABot Voice Edition is running...")
        app.run_polling()
