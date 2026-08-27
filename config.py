import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
LANGUAGE = os.getenv("LANGUAGE", "en-th")

# Unified Model Configuration Structure
MODEL_CONFIG = {
    "GEMINI_CONFIG": {
        "primary": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        "fallback": os.getenv("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash"),
        "vision": os.getenv("GEMINI_VISION_MODEL", "gemini-1.5-flash"),
    },
    "OPENROUTER": {
        "primary": os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free"),
        "reasoning": os.getenv("OPENROUTER_REASONING_MODEL", "meta-llama/llama-3.1-8b-instruct:free"),
    }
}

def validate_config():
    """Validate that configured models are free."""
    from ai.model_registry import is_model_free
    
    logger.info("Checking OpenRouter configuration...")
    
    # Check OPENROUTER models only
    models = MODEL_CONFIG.get("OPENROUTER", {})
    for key, model_id in models.items():
        if not is_model_free(model_id):
            error_msg = f"ERROR: Configured model '{model_id}' is not free. Paid models are not allowed."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    logger.info("✓ All configured OpenRouter models are free.")

# Run validation on import
try:
    if OPENROUTER_API_KEY:
        validate_config()
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
