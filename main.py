import os
import threading
import telebot
import time
from flask import Flask, jsonify
from handlers.message_handler import init_handlers

# ==========================================
# 1. Flask Health Check Server
# ==========================================
app = Flask(__name__)

# Keep reference to bot thread
bot_thread = None
polling_started = False

@app.route('/')
def root():
    return "iKALABot is running live!", 200

@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "service": "iKALABot",
        "telegram_polling": "active" if bot_thread and bot_thread.is_alive() else "inactive"
    }), 200

# ==========================================
# 2. Telegram Bot Setup
# ==========================================
def run_bot(token):
    global polling_started
    import os
    pid = os.getpid()
    
    if polling_started:
        print(f"[Telegram][CRITICAL] Duplicate polling startup prevented. PID={pid}")
        return
    
    polling_started = True
    print(f"[Telegram] Polling started. PID={pid}")
    
    try:
        bot = telebot.TeleBot(token)
        init_handlers(bot)

        print("Clearing old webhooks...")
        bot.remove_webhook()
        print("Starting Telegram Bot Polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
    except Exception as e:
        error_msg = str(e)
        if "409" in error_msg or "Conflict" in error_msg:
            print(f"[Telegram][CRITICAL] 409 Conflict detected. PID={pid}")
            print("[Telegram][CRITICAL] Another getUpdates consumer is active.")
            print("[Telegram][CRITICAL] Polling stopped; no automatic retry.")
            return
        
        print(f"[Polling Error]: {e}. Restarting in 5s...")
        polling_started = False
        time.sleep(5)
        run_bot(token)

def run_web(port):
    # Disable reloader to prevent double polling
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def main():
    global bot_thread
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
