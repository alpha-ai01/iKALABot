import os
import logging

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

# Unified Model Configuration Structure
# Force valid models to avoid environment variable overrides of invalid/paid models
MODEL_CONFIG = {
    "GOOGLE": {
        "primary": "gemini-1.5-flash",
        "fallback": "gemini-1.5-flash",
        "vision": "gemini-1.5-flash",
    },
    "OPENROUTER": {
        "primary": "nvidia/nemotron-3.5-lightning:free",
        "reasoning": "thinkingmachines/inkling:free",
    }
}

def validate_config():
    """Validate that configured models are free."""
    from ai.model_registry import is_model_free
    
    logger.info("Checking OpenRouter configuration...")
    
    # Check OPENROUTER models
    for provider, models in MODEL_CONFIG.items():
        if provider == "OPENROUTER":
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

