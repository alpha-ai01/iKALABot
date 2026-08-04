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

# Primary Client
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Fallback Client
openrouter_client = None
if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

# ---------------------------------------------------------
# Helper Function: Split Long Messages for Telegram (Max 4000 chars)
# ---------------------------------------------------------
def send_long_message(message_obj, text):
    """ตัดแบ่งข้อความตอบกลับหากยาวเกินขีดจำกัดของ Telegram"""
    max_length = 4000
    if len(text) <= max_length:
        bot.reply_to(message_obj, text)
        return

    # แบ่งส่งเป็นส่วนๆ
    for i in range(0, len(text), max_length):
        chunk = text[i:i + max_length]
        bot.send_message(message_obj.chat.id, chunk)
        time.sleep(0.5)

# ---------------------------------------------------------
# Helper Function: OpenRouter Fallback
# ---------------------------------------------------------
def ask_openrouter_fallback(prompt_text):
    if not openrouter_client:
        return "⚠️ [Fallback Error]: OPENROUTER_API_KEY is missing."
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
# Message Handlers
# ---------------------------------------------------------
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🤖 iKALABot Ready! (Pure Polling Mode)\n"
        "- Primary Model: gemini-3.6-flash\n"
        "- Fallback Model: meta-llama/llama-3.1-8b-instruct (OpenRouter)"
    )

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    user_prompt = message.text
    print(f"=== Received Prompt Length: {len(user_prompt)} chars ===")
    
    # 1. Primary Route: Gemini 3.6 Flash
    if gemini_client:
        try:
            res = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_prompt
            )
            if res.text:
                send_long_message(message, res.text)
                return
            else:
                print("[Gemini Warning]: Empty text response returned.")
        except Exception as e:
            print(f"[Gemini Exception Log]: {e}")

    # 2. Fallback Route: OpenRouter (Llama 3.1 8B Instruct)
    print("--> Triggering OpenRouter Fallback...")
    fallback_response = ask_openrouter_fallback(user_prompt)
    send_long_message(message, fallback_response)

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=== Starting Pure Polling Bot with Long Message Support ===")
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"[Warning] remove_webhook: {e}")

    bot.infinity_polling(skip_pending=True)
