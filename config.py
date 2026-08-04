import os

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Updated Default Models
DEFAULT_OPENROUTER_MODEL = "openai/o4-mini"
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
DEFAULT_GEMINI_VISION_MODEL = "gemini-3.1-flash-image"
DEFAULT_X_SEARCH_MODEL = "x-ai/grok-4.1-fast"
