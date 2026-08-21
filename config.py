import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# AI Models Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite")
VOICE_GEMINI_MODEL = os.getenv("VOICE_GEMINI_MODEL", "gemini-3.1-flash-lite")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

DEFAULT_GEMINI_VISION_MODEL = GEMINI_MODEL  # Using primary as default for vision
DEFAULT_X_SEARCH_MODEL = "x-ai/grok-4.1-fast"

