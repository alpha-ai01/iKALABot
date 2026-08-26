import telebot
import os
import sys

def cleanup():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)
        
    bot = telebot.TeleBot(token)
    try:
        print("Attempting to delete webhook and clear pending updates...")
        # delete_webhook drops any webhook set on the Telegram server
        bot.delete_webhook(drop_pending_updates=True)
        print("Webhook deleted and pending updates cleared successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cleanup()
