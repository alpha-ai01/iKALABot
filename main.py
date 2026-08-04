import os
import sys
import time
import telebot
from google import genai
from openai import OpenAI

# ---------------------------------------------------------
# 1. Environment & Security Checks
# ---------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    print("[CRITICAL ERROR]: Missing TELEGRAM_BOT_TOKEN!")
    sys.exit(1)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Primary Client (Gemini Direct)
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Fallback Client (OpenRouter Gateway)
openrouter_client = None
if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

# ---------------------------------------------------------
# Helper Function: Message Chunking for Telegram (Max 4000 chars)
# ---------------------------------------------------------
def send_long_message(message_obj, text):
    max_length = 4000
    if len(text) <= max_length:
        bot.reply_to(message_obj, text)
        return

    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]
        bot.send_message(message_obj.chat.id, chunk)
        time.sleep(0.5)

# ---------------------------------------------------------
# Helper Function: OpenRouter Fallback
# ---------------------------------------------------------
def ask_openrouter_fallback(prompt_text):
    if not openrouter_client:
        return "⚠️ [Fallback Error]: OPENROUTER_API_KEY is not configured on Render."
    try:
        response = openrouter_client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": prompt_text}],
            extra_headers={
                "HTTP-Referer": "https://render.com",
                "X-Title": "iKALABot"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ [Fallback Exception]: {e}"

# ---------------------------------------------------------
# Telegram Handlers
# ---------------------------------------------------------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🤖 iKALABot Active!\n"
        "- Primary: gemini-3.6-flash\n"
        "- Fallback: meta-llama/llama-3.1-8b-instruct (OpenRouter)"
    )

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    user_prompt = message.text
    
    # 1. Try Primary Model: Gemini 3.6 Flash
    if gemini_client:
        try:
            res = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_prompt
            )
            if res.text:
                send_long_message(message, res.text)
                return
        except Exception as e:
            # Catch 429 Quota Exhausted, 503 Overload, or any API Exception
            print(f"[Gemini API Exception]: {e} -> Auto-fallback to OpenRouter...")

    # 2. Fallback Model: OpenRouter Llama 3.1 8B Instruct
    bot.reply_to(
        message, 
        "⚠️ [Notice]: Gemini Quota/Rate Limit Exceeded (429). Switching to OpenRouter (Llama 3.1 8B Instruct)..."
    )
    fallback_response = ask_openrouter_fallback(user_prompt)
    send_long_message(message, fallback_response)

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=== Starting main.py in Pure Polling Mode with Auto-Fallback ===")
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"[Warning] Webhook cleanup: {e}")

    bot.infinity_polling(skip_pending=True)
