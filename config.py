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

import json

# Load Model Configuration
def load_model_config():
    config_path = "config/models.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    
    return config

MODEL_CONFIG = load_model_config()

def validate_config():
    """Validate that configured models are free."""
    from ai.model_registry import is_model_free
    
    logger.info("Checking OpenRouter configuration...")
    
    # Check OPENROUTER models
    models = MODEL_CONFIG.get("openrouter", {})
    for key, model_id in models.items():
        if not is_model_free(model_id):
            error_msg = f"ERROR: Configured model '{model_id}' is not free. Paid models are not allowed."
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    logger.info("✓ All configured OpenRouter models are free.")

import sys

# Run validation on import
try:
    if OPENROUTER_API_KEY:
        validate_config()
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
    sys.exit(1)
