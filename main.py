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
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# 3. Message Handlers
# ==========================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "สวัสดีครับ iKALABot พร้อมทำงานแล้วครับ!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = execute_task('chat', message.text)
        bot.reply_to(message, str(reply))
    except Exception as e:
        print(f"[Message Error]: {e}")
        bot.reply_to(message, "ขออภัยครับ เกิดข้อผิดพลาดในการประมวลผล")

@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice_message(message):
    try:
        reply = handle_voice(bot, message)
        bot.reply_to(message, str(reply))
    except Exception as e:
        print(f"[Voice Error]: {e}")
        bot.reply_to(message, "ขออภัยครับ เกิดข้อผิดพลาดในการประมวลผลเสียง")

# ==========================================
# 4. Main Execution
# ==========================================
def run_bot():
    print("Starting Telegram Bot Polling...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)

if __name__ == "__main__":
    # Start bot in a thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask server in the main thread
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
