import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

# Unified Model Configuration Structure
MODEL_CONFIG = {
    "GOOGLE": {
        "primary": os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        "fallback": os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash-lite"),
        "vision": os.getenv("GEMINI_VISION_MODEL", "gemini-3.1-flash-lite"),
    },
    "OPENROUTER": {
        "primary": os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free"),
        "reasoning": os.getenv("OPENROUTER_REASONING_MODEL", "thinkingmachines/inkling:free"),
    }
}

