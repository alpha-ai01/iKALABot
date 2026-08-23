import os
import threading
import telebot
import time
import logging
from flask import Flask, jsonify
from handlers.message_handler import init_handlers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 1. Flask Health Check Server
# ==========================================
app = Flask(__name__)

@app.route('/')
def root():
    return "iKALABot is running live!", 200

@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "service": "iKALABot"
    }), 200

# ==========================================
# 2. Telegram Bot Setup
# ==========================================
def run_bot(token):
    bot = telebot.TeleBot(token)
    init_handlers(bot)

    retry_delay = 5  # Start with 5 seconds

    while True:
        try:
            logger.info("Clearing old webhooks...")
            bot.remove_webhook()
            logger.info("Starting Telegram Bot Polling...")
            
            # Reset retry delay on successful start
            retry_delay = 5
            
            bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True, none_stop=True)
        except Exception as e:
            logger.error(f"[Polling Error]: {e}")
            logger.info(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            # Exponential backoff
            retry_delay = min(retry_delay * 2, 600)  # Max 10 mins

def run_web(port):
    # Disable reloader to prevent double polling
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def main():
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if BOT_TOKEN:
        # Start bot in a background thread
        bot_thread = threading.Thread(
            target=run_bot,
            args=(BOT_TOKEN,),
            name="telegram-polling",
            daemon=True
        )
        bot_thread.start()
    else:
        logger.warning("TELEGRAM_BOT_TOKEN not set, skipping Telegram Bot")

    port = int(os.environ.get("PORT", 10000))
    run_web(port)

if __name__ == "__main__":
    main()
