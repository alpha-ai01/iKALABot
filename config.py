import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Render จะส่งพอร์ตเข้ามาทาง Environment Variable $PORT
PORT = int(os.getenv("PORT", 10000))
