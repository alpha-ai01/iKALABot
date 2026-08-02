import os
import requests
import uvicorn
from fastapi import FastAPI, Request
from utils.logger import logger
import config
from utils.tools import get_current_time, search_web
from ai.openrouter import ask_openrouter

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
        
        # 1. คำสั่งดูเวลา
        if text.startswith("/time"):
            send_message(chat_id, get_current_time())
            
        # 2. คำสั่งค้นหาเว็บ
        elif text.startswith("/search"):
            query = text.replace("/search", "").strip()
            if query:
                send_message(chat_id, search_web(query))
            else:
                send_message(chat_id, "กรุณาพิมพ์คำที่ต้องการค้นหาต่อท้าย เช่น /search อากาศวันนี้")
                
        # 3. คำสั่งเริ่มต้น
        elif text.startswith("/start"):
            send_message(chat_id, "สวัสดีครับ! iKALABot พร้อมใช้งานแล้ว\n- พิมพ์ /time เพื่อดูเวลา\n- พิมพ์ /search [คำค้น] เพื่อหาข้อมูล\n- หรือพิมพ์ข้อความทั่วไปเพื่อคุยกับ AI ได้เลยครับ")
            
        # 4. ข้อความทั่วไป -> ส่งให้ AI ตอบ
        else:
            ai_response = ask_openrouter(text)
            send_message(chat_id, ai_response)

    return {"status": "ok"}

def send_message(chat_id, text):
    if not config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing!")
        return
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        logger.error(f"Error sending message: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
