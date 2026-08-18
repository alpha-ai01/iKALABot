import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Updated Default Models
# Use OpenRouter free router by default (free access per project request)
DEFAULT_OPENROUTER_MODEL = "openrouter/free"
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
DEFAULT_GEMINI_VISION_MODEL = "gemini-3.1-flash-image"
DEFAULT_X_SEARCH_MODEL = "x-ai/grok-4.1-fast"
