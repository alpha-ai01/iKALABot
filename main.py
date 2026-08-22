import os
import threading
import telebot
from flask import Flask, jsonify
from handlers.message_handler import init_handlers

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

    try:
        print("Clearing old webhooks...")
        bot.remove_webhook()
        print("Starting Telegram Bot Polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
    except Exception as e:
        print(f"[Polling Error]: {e}")

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
        print("TELEGRAM_BOT_TOKEN not set, skipping Telegram Bot")

    port = int(os.environ.get("PORT", 10000))
    run_web(port)

if __name__ == "__main__":
    main()
