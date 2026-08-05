import logging
import sys

logging.basicConfig(level=logging.INFO)


def main():
    try:
        # Delayed imports so startup failures are captured by outer try/except
        import os
        import threading
        from flask import Flask
        import telebot

        # Local imports that may raise should happen here to show traceback in logs
        from dispatcher import execute_task
        from handlers.voice_handler import handle as handle_voice
        from ai.telegram_utils import safe_send_text
        from ai import openrouter_api, gemini_api  # keep available for warm imports

        # ==========================================
        # Flask Server (Health Check)
        # ==========================================
        app = Flask(__name__)

        @app.route('/')
        def health_check():
            return "iKALABot is running live!", 200

        # ==========================================
        # Telegram
        # ==========================================
        BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        bot = None

        if BOT_TOKEN:
            bot = telebot.TeleBot(BOT_TOKEN)

            # ==========================================
            # Telegram Message Handlers (registered only when bot is available)
            # ==========================================
            @bot.message_handler(commands=['start', 'help'])
            def send_welcome(message):
                # short welcome message is safe to send directly via safe_send_text
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

        def run_bot():
            # If bot is not configured, skip polling but keep Flask health check running
            if not bot:
                print("[INFO] TELEGRAM_BOT_TOKEN not set. Telegram bot disabled; running health check only.")
                return

            # resilient polling loop: restart polling on unexpected exceptions
            import time
            while True:
                try:
                    try:
                        print("Clearing old webhooks...")
                        bot.remove_webhook()
                    except Exception as e:
                        # non-fatal; continue to polling
                        print(f"[Webhook clear warning]: {e}")

                    print("Starting Telegram Bot Polling...")
                    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
                except Exception as e:
                    print(f"[Polling Error]: {e}")
                    # small delay before retrying to avoid tight crash loops
                    time.sleep(5)

        # Start bot in background thread so Flask can serve health checks
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()

        # Run Flask app
        port = int(os.environ.get("PORT", 10000))
        app.run(host="0.0.0.0", port=port)

    except Exception:
        # Re-raise to be caught by outer handler with full traceback
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Startup failure — uncaught exception")
        sys.exit(1)
