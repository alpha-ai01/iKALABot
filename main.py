import os
import threading
import http.server
import socketserver
import telebot
from google import genai
import requests
import json
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from gtts import gTTS

PORT = int(os.environ.get("PORT", 8080))
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class SafeLogFormatter(logging.Formatter):
    def format(self, record):
        log_msg = super().format(record)
        if TELEGRAM_BOT_TOKEN: log_msg = log_msg.replace(TELEGRAM_BOT_TOKEN, "[HIDDEN_BOT_TOKEN]")
        if OPENROUTER_API_KEY: log_msg = log_msg.replace(OPENROUTER_API_KEY, "[HIDDEN_OR_KEY]")
        if GEMINI_API_KEY: log_msg = log_msg.replace(GEMINI_API_KEY, "[HIDDEN_GEMINI_KEY]")
        return log_msg

logger = logging.getLogger("iKALABot")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(SafeLogFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"iKALABot Super Full Options is running!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        httpd.serve_forever()

def clean_text_for_bot(text):
    cleaned = text.replace('*', '').replace('#', '').replace('_', '').replace('`', '')
    return cleaned.strip()

# เก็บประวัติการสนทนาแยกตาม chat_id (Memory)
chat_histories = {}

def get_system_context(chat_id):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history = chat_histories.get(chat_id, [])
    history_str = "\n".join([f"{item['role']}: {item['text']}" for item in history[-6:]]) # จำ 6 ข้อย้อนหลัง
    
    return (
        f"[System Info: Current time is {now}. You are iKALABot. "
        f"STRICT RULE: Do NOT use markdown symbols like asterisks (*), hashes (#), underscores (_), or backticks (`). Plain text only.]\n\n"
        f"Conversation History:\n{history_str}\n"
    )

def add_to_history(chat_id, role, text):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    chat_histories[chat_id].append({"role": role, "text": text})
    if len(chat_histories[chat_id]) > 20:
        chat_histories[chat_id].pop(0)

if not TELEGRAM_BOT_TOKEN:
    logger.error("ERROR: TELEGRAM_BOT_TOKEN not found")
else:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        chat_id = message.chat.id
        chat_histories[chat_id] = [] # ล้างความจำเมื่อเริ่มใหม่
        welcome_text = "iKALABot Memory Enabled\n\nSend text or voice messages. I will remember our conversation."
        bot.reply_to(message, welcome_text)

    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        chat_id = message.chat.id
        text = message.text
        bot.send_chat_action(message.chat.id, 'typing')
        
        add_to_history(chat_id, "User", text)
        prompt = f"{get_system_context(chat_id)}\nUser query: {text}"
        
        try:
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )
            final_reply = clean_text_for_bot(response.text)
            add_to_history(chat_id, "Model", final_reply)
            bot.reply_to(message, final_reply)
        except Exception as e:
            logger.error(f"Gemini Error: {str(e)}")
            bot.reply_to(message, "Error processing request")

    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice(message):
        chat_id = message.chat.id
        bot.send_chat_action(message.chat.id, 'record_audio')
        try:
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            temp_audio_path = "temp_voice.ogg"
            with open(temp_audio_path, 'wb') as f:
                f.write(downloaded_file)
            
            audio_file_ref = gemini_client.files.upload(file=temp_audio_path)
            
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[
                    audio_file_ref, 
                    f"{get_system_context(chat_id)}\nListen to this voice message, consider history, and provide ONLY the direct answer in plain text."
                ]
            )
            
            reply_text = clean_text_for_bot(response.text)
            add_to_history(chat_id, "User", "[Voice Message]")
            add_to_history(chat_id, "Model", reply_text)
            
            bot.reply_to(message, reply_text)

            bot.send_chat_action(message.chat.id, 'record_audio')
            tts = gTTS(text=reply_text, lang='th')
            reply_audio_path = "reply_voice.ogg"
            tts.save(reply_audio_path)

            with open(reply_audio_path, 'rb') as audio:
                bot.send_voice(message.chat.id, audio)

            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            if os.path.exists(reply_audio_path):
                os.remove(reply_audio_path)

        except Exception as e:
            logger.error(f"Voice Error: {str(e)}")
            bot.reply_to(message, "Voice processing error")

    if __name__ == "__main__":
        threading.Thread(target=run_server, daemon=True).start()
        logger.info("Removing old webhook and connecting to Telegram...")
        try:
            bot.remove_webhook()
        except Exception:
            pass
        logger.info("Telegram Bot is starting polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
