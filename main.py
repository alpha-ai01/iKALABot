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

def ask_openrouter(text):
    if not OPENROUTER_API_KEY:
        return "❌ Missing OPENROUTER_API_KEY"
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "google/gemma-2-9b-it:free",
                "messages": [{"role": "user", "content": text}]
            })
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ OpenRouter Error ({response.status_code})"
    except Exception as e:
        logger.error(f"OpenRouter Error: {str(e)}")
        return f"❌ OpenRouter Error: {str(e)}"

def get_system_context():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[System Info: Current time is {now}. You are iKALABot, a high-level multi-functional assistant.]"

if not TELEGRAM_BOT_TOKEN:
    logger.error("ERROR: TELEGRAM_BOT_TOKEN not found")
else:
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "🤖 **iKALABot Super Full Options**\n\n"
            "💬 **Text / URL Link:** Chat, search info, and read web pages\n"
            "🎙️ **Voice:** Transcribe and reply automatically\n"
            "📸 **Photo:** Multimodal image analysis\n"
            "📁 **Document / Script:** Review, format code, and add comments\n"
            "🤖 **Commands /ai or /llama:** Backup OpenRouter AI"
        )
        bot.reply_to(message, welcome_text)

    @bot.message_handler(commands=['ai', 'llama'])
    def handle_openrouter_cmd(message):
        text = message.text.replace('/ai', '').replace('/llama', '').strip()
        if not text:
            bot.reply_to(message, "Please provide text after command, e.g. /ai hello")
            return
        bot.send_chat_action(message.chat.id, 'typing')
        bot.reply_to(message, f"🤖 **OpenRouter (Gemma 2):**\n{ask_openrouter(text)}")

    @bot.message_handler(content_types=['text'])
    def handle_text(message):
        text = message.text
        bot.send_chat_action(message.chat.id, 'typing')
        
        if "http://" in text or "https://" in text:
            try:
                bot.reply_to(message, "🔍 Fetching content from URL...")
                url_extracted = text.split()[0]
                web_res = requests.get(url_extracted, timeout=5)
                soup = BeautifulSoup(web_res.text, 'html.parser')
                web_text = soup.get_text()[:3000]
                text = f"Please summarize and analyze this web content:\n{web_text}"
            except Exception as e:
                logger.warning(f"URL Read Error: {str(e)}")

        prompt = f"{get_system_context()}\nUser query: {text}"
        
        if not gemini_client:
            bot.reply_to(message, "⚠️ Gemini API Key missing. Switching to OpenRouter...\n\n" + ask_openrouter(text))
            return
            
        try:
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
            )
            bot.reply_to(message, response.text)
        except Exception as e:
            logger.error(f"Gemini Error: {str(e)}")
            fallback_msg = f"⚠️ Gemini error. Switching to OpenRouter...\n\n🤖:\n{ask_openrouter(text)}"
            bot.reply_to(message, fallback_msg)

    @bot.message_handler(content_types=['voice', 'audio'])
    def handle_voice(message):
        bot.send_chat_action(message.chat.id, 'record_audio')
        try:
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            temp_audio_path = "temp_voice.ogg"
            with open(temp_audio_path, 'wb') as f:
                f.write(downloaded_file)
            
            bot.reply_to(message, "🎙️ Transcribing and processing voice with Gemini...")
            audio_file_ref = gemini_client.files.upload(file=temp_audio_path)
            
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[
                    audio_file_ref, 
                    f"{get_system_context()}\nListen to this voice file, transcribe it, and fulfill the request inside."
                ]
            )
            
            bot.reply_to(message, f"🗣️ **Voice Transcription & Result:**\n\n{response.text}")
            
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
        except Exception as e:
            logger.error(f"Voice Error: {str(e)}")
            bot.reply_to(message, f"❌ Voice processing error: {str(e)}")

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            temp_img_path = "temp_image.jpg"
            with open(temp_img_path, 'wb') as f:
                f.write(downloaded_file)
                
            img_ref = gemini_client.files.upload(file=temp_img_path)
            response = gemini_client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[img_ref, f"{get_system_context()}\nAnalyze this image in detail and explain everything clearly."]
            )
            
            bot.reply_to(message, f"📸 **Image Analysis Result:**\n\n{response.text}")
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
        except Exception as e:
            logger.error(f"Photo Error: {str(e)}")
            bot.reply_to(message, f"❌ Cannot read image: {str(e)}")

    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        file_name = message.document.file_name
        bot.reply_to(message, f"📁 Processing file: {file_name}")
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            if file_name.endswith(('.py', '.js', '.txt', '.json', '.html', '.css', '.cpp', '.h', '.sql', '.sh', '.md', '.csv')):
                code_content = downloaded_file.decode('utf-8')[:6000]
                prompt = (
                    f"{get_system_context()}\n"
                    f"Content from script/document '{file_name}':\n\n{code_content}\n\n"
                    "Tasks:\n"
                    "1. Debug and check for errors\n"
                    "2. Format code cleanly\n"
                    "3. Add clear comments detailing each section"
                )
                
                response = gemini_client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
                bot.reply_to(message, f"🛠️ **Script Analysis & Formatting Result:**\n\n{response.text}")
            else:
                temp_doc_path = f"temp_{file_name}"
                with open(temp_doc_path, 'wb') as f:
                    f.write(downloaded_file)
                
                doc_ref = gemini_client.files.upload(file=temp_doc_path)
                response = gemini_client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[doc_ref, f"{get_system_context()}\nRead, summarize, and explain key details from this document."]
                )
                bot.reply_to(message, f"📄 **Document Summary ({file_name}):**\n\n{response.text}")
                
                if os.path.exists(temp_doc_path):
                    os.remove(temp_doc_path)
                    
        except Exception as e:
            logger.error(f"Document Error: {str(e)}")
            bot.reply_to(message, f"❌ File processing error: {str(e)}")

    if __name__ == "__main__":
        threading.Thread(target=run_server, daemon=True).start()
        logger.info("Removing old webhook and connecting to Telegram...")
        try:
            bot.remove_webhook()
        except Exception:
            pass
        logger.info("Telegram Bot is starting polling...")
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
