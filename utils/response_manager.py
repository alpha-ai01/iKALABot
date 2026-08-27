import os
import logging
import sqlite3
from telebot import TeleBot
from voice.text_to_speech import text_to_speech
from utils.text_utils import clean_ai_response

# Preferences database to handle /voice_on /voice_off
PREFS_DB = "user_prefs.db"

def init_prefs_db():
    with sqlite3.connect(PREFS_DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS voice_prefs (
                user_id TEXT PRIMARY KEY,
                voice_enabled BOOLEAN
            )
        """)

def is_voice_enabled(user_id: str) -> bool:
    with sqlite3.connect(PREFS_DB) as conn:
        cursor = conn.execute("SELECT voice_enabled FROM voice_prefs WHERE user_id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row[0] if row else True # Default True

def set_voice_enabled(user_id: str, enabled: bool):
    with sqlite3.connect(PREFS_DB) as conn:
        conn.execute("INSERT OR REPLACE INTO voice_prefs (user_id, voice_enabled) VALUES (?, ?)", (str(user_id), enabled))

def send_ai_response(bot: TeleBot, message, response_text: str):
    """
    Centralized response sender that handles text and voice.
    Split long text responses into multiple messages to avoid Telegram limits.
    """
    MAX_LENGTH = 4000
    
    # 1. Send Text (Split if necessary)
    if len(response_text) > MAX_LENGTH:
        # Split by newlines if possible, otherwise by character count
        parts = []
        lines = response_text.split('\n')
        current_part = ""
        for line in lines:
            if len(current_part) + len(line) + 1 > MAX_LENGTH:
                parts.append(current_part)
                current_part = line
            else:
                current_part = (current_part + '\n' + line) if current_part else line
        if current_part:
            parts.append(current_part)
        
        for part in parts:
            if part.strip():
                bot.reply_to(message, part)
    else:
        bot.reply_to(message, response_text)
    
    # 2. TTS (Always attempted, failure shouldn't stop text delivery)
    try:
        # Clean text for TTS
        tts_text = clean_ai_response(response_text)
        audio_path = text_to_speech(tts_text)
        
        if audio_path:
            with open(audio_path, "rb") as audio:
                bot.send_voice(message.chat.id, audio)
            
            # Cleanup
            if os.path.exists(audio_path):
                os.remove(audio_path)
    except Exception as e:
        logging.error("TTS failed in response manager: %s", str(e))
