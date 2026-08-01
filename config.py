import os

# รองรับทั้ง TELEGRAM_TOKEN และ TELEGRAM_BOT_TOKEN
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

PORT = int(os.getenv("PORT", 10000))
