import tempfile
import logging
from telebot.apihelper import ApiTelegramException

MAX_TG_LEN = 4000


def safe_send_text(bot, chat_id, text, reply_to_message=None, max_len=MAX_TG_LEN, **kwargs):
    """Send text to Telegram safely.

    - If text length <= max_len: send_message
    - Else: split into chunks and send sequentially
    - If Telegram still rejects due to length, fall back to sending as a .txt file
    """
    try:
        if not isinstance(text, str):
            text = str(text)

        if len(text) <= max_len:
            return bot.send_message(chat_id, text, reply_to_message=reply_to_message, **kwargs)

        # Send in chunks
        for i in range(0, len(text), max_len):
            part = text[i : i + max_len]
            try:
                bot.send_message(chat_id, part, reply_to_message=reply_to_message, **kwargs)
            except ApiTelegramException as e:
                err = str(e).lower()
                if "message is too long" in err:
                    # Fallback: write full text to temp file and send as document
                    with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
                        f.write(text)
                        path = f.name
                    with open(path, "rb") as fh:
                        return bot.send_document(chat_id, fh, caption="ผลลัพธ์ (ไฟล์แนบ)")
                raise
        return True
    except ApiTelegramException:
        # propagate telebot-specific exceptions
        raise
    except Exception as e:
        logging.error("[Telegram utils] safe_send_text error: %s", str(e)[:300])
        raise
