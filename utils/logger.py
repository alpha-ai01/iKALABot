import logging
from config import TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, OPENROUTER_API_KEY

class SafeFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        keys = [k for k in [TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, OPENROUTER_API_KEY] if k and k != ""]
        for key in keys:
            if key in msg:
                msg = msg.replace(key, "***[REDACTED_API_KEY]***")
        return msg

logger = logging.getLogger("SecureBotLogger")
handler = logging.StreamHandler()
handler.setFormatter(SafeFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
