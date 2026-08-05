import os
from dispatcher import execute_task
from handlers.voice_handler import handle as handle_voice
import threading
from flask import Flask
import telebot
import tempfile

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
    safe_send_text(bot, message.chat.id, reply, reply_to_message=message)
    

# ==========================================
# 6. รันระบบ Multi-Threading (ล้าง Webhook ป้องกัน Error 409)
# ==========================================


@bot.message_handler(content_types=['voice','audio'])
def receive_voice(message):
    reply = handle_voice(bot, message)
    bot.reply_to(message, reply)


def run_bot():
    try:
        print("Clearing old webhooks...")
        bot.remove_webhook()
        print("Starting Telegram Bot Polling...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
    except Exception as e:
        print(f"[Polling Error]: {e}")

if __name__ == "__main__":

    from telebot.apihelper import ApiTelegramException

MAX_TG_LEN = 4000

def _chunks(s, n):
    for i in range(0, len(s), n):
        yield s[i:i+n]

def safe_send_text(bot, chat_id, text, reply_to_message=None, **kwargs):
    try:
        if len(text) <= MAX_TG_LEN:
            return bot.send_message(chat_id, text, reply_to_message=reply_to_message, **kwargs)
        # ถ้าไม่เกินจำนวนชิ้นที่รับได้ ให้แยกส่ง
        for part in _chunks(text, MAX_TG_LEN):
            bot.send_message(chat_id, part, reply_to_message=reply_to_message, **kwargs)
        return True
    except ApiTelegramException as e:
        # ถ้าเกิดข้อผิดพลาดเกี่ยวกับความยาวอีกครั้ง ให้ส่งเป็นไฟล์แทน
        err = str(e)
        if "message is too long" in err.lower():
            with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
                f.write(text)
                path = f.name
            with open(path, "rb") as fh:
                return bot.send_document(chat_id, fh, caption="ผลลัพธ์ (ไฟล์แนบ)")
        raise
            bot_thread = threading.Thread(target=run_bot, daemon=True)
            bot_thread.start()

            port = int(os.environ.get("PORT", 10000))
    def run_bot():
            bot.infinity_polling()

            threading.Thread(target=run_bot).start()

            app.run(host="0.0.0.0", port=10000)
    
            
       
    from flask import Flask
            app = Flask(__name__)

            @app.route("/")
    def home():
       
        return "Bot Running"

    if __name__ == "__main__":
            app.run(host="0.0.0.0", port=10000)
        
            app.run()
        
            
        print("Bot Started")

    
    
