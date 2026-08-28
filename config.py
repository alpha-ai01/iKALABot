import os
import logging
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
LANGUAGE = os.getenv("LANGUAGE", "en-th")

# Load Model Configuration
def load_model_config():
    # Use absolute path to ensure it works from any directory
    base_path = Path(__file__).parent
    config_path = base_path / "config/models.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    
    return config

MODEL_CONFIG = load_model_config()

# Validate and set specific model constants
if "gemini" not in MODEL_CONFIG or "audio" not in MODEL_CONFIG["gemini"]:
    raise RuntimeError("Missing required model configuration: gemini.audio in config/models.json")

VOICE_GEMINI_MODEL = MODEL_CONFIG["gemini"]["audio"]

def validate_config():
    """Validate that configured models are free if possible."""
    if not OPENROUTER_API_KEY:
        logger.info("OpenRouter API Key not set. Skipping OpenRouter validation.")
        return

    from ai.model_registry import is_model_free
    
    logger.info("Checking OpenRouter configuration...")
    
    # Check OPENROUTER models
    models = MODEL_CONFIG.get("openrouter", {})
    for key, model_id in models.items():
        if not is_model_free(model_id):
            # Log as warning instead of raising exception to prevent startup crash
            logger.warning(f"WARNING: Configured OpenRouter model '{model_id}' is not free or cannot be verified.")
        else:
            logger.info(f"✓ OpenRouter model '{model_id}' verified as free.")

# Run validation on import
if OPENROUTER_API_KEY:
    try:
        validate_config()
    except Exception as e:
        logger.error(f"Configuration validation encountered an issue: {e}")
