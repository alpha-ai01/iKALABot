import os
import sys
import time
import threading
import telebot
from flask import Flask
from google import genai
from openai import OpenAI

# ---------------------------------------------------------
# Dummy Web Server for Render Web Service Health Check
# ---------------------------------------------------------
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return "OK - Bot is running", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---------------------------------------------------------
# Bot Initialization
# ---------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    print("[CRITICAL ERROR]: Missing TELEGRAM_BOT_TOKEN!")
    sys.exit(1)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

openrouter_client = None
if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

def send_long_message(message_obj, text):
    max_length = 4000
    if len(text) <= max_length:
        bot.reply_to(message_obj, text)
        return
    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]
        bot.send_message(message_obj.chat.id, chunk)
        time.sleep(0.5)

def ask_openrouter_fallback(prompt_text):
    if not openrouter_client:
        return "⚠️ [Fallback Error]: OPENROUTER_API_KEY is missing."
    try:
        response = openrouter_client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": prompt_text}],
            extra_headers={"HTTP-Referer": "https://render.com", "X-Title": "iKALABot"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ [Fallback Exception]: {e}"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🤖 iKALABot Active!\n"
        "- Primary: gemini-3.6-flash\n"
        "- Fallback: meta-llama/llama-3.1-8b-instruct (OpenRouter)"
    )

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    user_prompt = message.text
    if gemini_client:
        try:
            res = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_prompt
            )
            if res.text:
                send_long_message(message, res.text)
                return
        except Exception as e:
            print(f"[Gemini Exception]: {e} -> Switching to OpenRouter...")

    bot.reply_to(message, "⚠️ [Notice]: Gemini limit/error. Switching to OpenRouter...")
    fallback_response = ask_openrouter_fallback(user_prompt)
    send_long_message(message, fallback_response)

if __name__ == "__main__":
    # รัน Web Server เป็น Background Thread เพื่อตอบสนอง Render Health Check
    threading.Thread(target=run_web_server, daemon=True).start()
    
    # เคลียร์ Webhook เก่า
    try:
        bot.remove_webhook()
        time.sleep(2)
    except Exception as e:
        print(f"[Warning] Webhook cleanup: {e}")

    # Start Polling
    while True:
        try:
            print("[INFO] TeleBot starting infinity_polling...")
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"[Polling Exception Caught]: {e}")
            time.sleep(5)
