import os
import threading
import telebot
from flask import Flask
from dispatcher import execute_task
from handlers.voice_handler import handle as handle_voice

# ==========================================
# 1. Flask Health Check Server
# ==========================================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "iKALABot is running live!", 200

# ==========================================
# 2. Telegram Bot
# ==========================================
if __name__ == "__main__":
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    bot = telebot.TeleBot(BOT_TOKEN)
    # Start bot in a thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask server in the main thread
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
else:
    # Minimal bot initialization for imports
    bot = telebot.TeleBot("123456:dummy_token")
