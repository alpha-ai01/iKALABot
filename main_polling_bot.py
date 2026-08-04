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

# Initialize Clients
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Primary Model Client (Gemini Direct)
gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Fallback Model Client (OpenRouter)
openrouter_client = None
if OPENROUTER_API_KEY:
    openrouter_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

# ---------------------------------------------------------
# 2. OpenRouter Fallback Helper Function
# ---------------------------------------------------------
def ask_openrouter_fallback(prompt_text):
    """ส่ง Request ไปที่ OpenRouter โดยใช้ meta-llama/llama-3.1-8b-instruct"""
    if not openrouter_client:
        return "⚠️ [Fallback Error]: OPENROUTER_API_KEY is not set."
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
        return f"⚠️ [Fallback Failed]: {e}"

# ---------------------------------------------------------
# 3. Telegram Message Handlers
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
    
    # 1. ลองเรียกใช้ Gemini 3.6 Flash (Primary)
    if gemini_client:
        try:
            res = gemini_client.models.generate_content(
                model="gemini-3.6-flash",
                contents=user_prompt
            )
            bot.reply_to(message, res.text)
            return
        except Exception as e:
            # ดักจับทั้ง 503 UNAVAILABLE และ Error อื่นๆ ของ Gemini
            print(f"[Gemini Exception]: {e} -> Auto Switching to OpenRouter Fallback...")
    
    # 2. หาก Gemini มีปัญหา (เช่น 503 High Demand) จะ Auto-Fallback ไปยัง OpenRouter
    bot.reply_to(message, "⚠️ [System Notice]: Gemini is experiencing high demand (503). Auto-switching to Llama 3.1 8B Instruct via OpenRouter...")
    fallback_response = ask_openrouter_fallback(user_prompt)
    bot.reply_to(message, fallback_response)

# ---------------------------------------------------------
# 4. Pure Polling Execution with Conflict Prevention
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=== Starting Bot in Pure Polling Mode ===")
    
    # เคลียร์ Webhook เก่าออก ป้องกัน Error 409 Conflict
    try:
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"[Warning] Failed to remove webhook: {e}")

    print("Primary: gemini-3.6-flash | Fallback: meta-llama/llama-3.1-8b-instruct")
    
    # รัน Polling ยาวๆ
    bot.infinity_polling(skip_pending=True)
