import os
import time
import telebot

from ai.telegram_utils import safe_send_text
from dispatcher import execute_task
from handlers.voice_handler import handle as handle_voice

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("[ERROR] TELEGRAM_BOT_TOKEN not set. Worker will exit.")
    raise SystemExit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Register handlers
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    safe_send_text(bot, message.chat.id, "สวัสดีครับ iKALABot พร้อมทำงานแล้วครับ!", reply_to_message=message)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
    except Exception as e:
        print(f"[Chat Action Error]: {e}")

    try:
        reply = execute_task('chat', message.text)
    except Exception as e:
        reply = "เกิดข้อผิดพลาดขณะประมวลผลคำขอของคุณ"
        print(f"[Execute Task Error]: {e}")

    safe_send_text(bot, message.chat.id, reply, reply_to_message=message)

@bot.message_handler(content_types=['voice', 'audio'])
def receive_voice(message):
    try:
        reply = handle_voice(bot, message)
    except Exception as e:
        reply = "เกิดข้อผิดพลาดขณะประมวลผลเสียงของคุณ"
        print(f"[Voice Handler Error]: {e}")

    safe_send_text(bot, message.chat.id, reply, reply_to_message=message)


def run():
    # resilient polling loop
    while True:
        try:
            try:
                bot.remove_webhook()
            except Exception as e:
                print(f"[Webhook clear warning]: {e}")

            print("Starting Telegram Bot Polling (worker)...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
        except Exception as e:
            print(f"[Polling Error]: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run()
