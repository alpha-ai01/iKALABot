from fastapi import FastAPI, Request
from utils.logger import logger
import config
import requests

app = FastAPI()

@app.get("/")
@app.get("/health")
def health_check():
    logger.info("Health check ping received.")
    return {"status": "ok", "message": "Bot is running perfectly!"}

@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    logger.info(f"Received Telegram Update: {data}")
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        
        if text.startswith("/"):
            send_message(chat_id, f"Command received: {text} (Waiting for AI module...)")
        else:
            send_message(chat_id, f"Bot received: {text}")

    return {"status": "ok"}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error sending message: {e}")
