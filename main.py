import os
from dispatcher import execute_task
import threading
from flask import Flask
import telebot

# ==========================================
# 1. ตั้งค่า Flask Server (สำหรับ Render Health Check)
# ==========================================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "iKALABot is running live!", 200

# ==========================================
# 2. Telegram
# ==========================================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# 5. Telegram Message Handlers
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "สวัสดีครับ iKALABot พร้อมทำงานแล้วครับ!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
    except Exception as e:
        print(f"[Chat Action Error]: {e}")

    reply = execute_task('chat', message.text)
    bot.reply_to(message, reply)

# ==========================================
# 6. รันระบบ Multi-Threading (ล้าง Webhook ป้องกัน Error 409)
# ==========================================
def run_bot():
    try:
        print("Clearing old webhooks...")
        bot.remove_webhook()
        print("Starting Telegram Bot Polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
    except Exception as e:
        print(f"[Polling Error]: {e}")

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
