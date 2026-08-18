import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Updated Default Models
# Use a valid free model string for OpenRouter
DEFAULT_OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
# Use a valid, currently supported Gemini model
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
DEFAULT_GEMINI_VISION_MODEL = "gemini-1.5-flash"
DEFAULT_X_SEARCH_MODEL = "x-ai/grok-4.1-fast"
