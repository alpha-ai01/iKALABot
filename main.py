import sys
import telebot
from config import TELEGRAM_TOKEN, PORT
from web_server import start_web_server
from handlers import register_bot_handlers

if not TELEGRAM_TOKEN:
    print("Error: ไม่พบ TELEGRAM_TOKEN กรุณาตั้งค่าใน Environment Variables")
    sys.exit(1)

# 1. เริ่มรัน Web Server บน Thread แยก เพื่อรอรับ Request จาก UptimeRobot
print(f"Starting Web Server on port {PORT}...")
start_web_server(PORT)

# 2. เริ่มทำงาน Telegram Bot
print("Starting Telegram Bot...")
bot = telebot.TeleBot(TELEGRAM_TOKEN)
register_bot_handlers(bot)

# 3. รัน Polling
if __name__ == "__main__":
    print("Bot is successfully running!")
    bot.infinity_polling()
