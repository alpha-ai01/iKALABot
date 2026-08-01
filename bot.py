import os
import telebot
import requests
import base64
import re
import time
from flask import Flask
from threading import Thread
from gtts import gTTS

app = Flask('')
@app.route('/')
def home():
    return "Bot is running on Singapore!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

TOKEN = os.environ.get('TELEGRAM_TOKEN')
API_KEY = os.environ.get('OPENROUTER_API_KEY')

bot = telebot.TeleBot(TOKEN)

# ฟังก์ชันดึงเนื้อหาจาก URL หรือสคริปต์เชิงลึก
def extract_url_content(text: str) -> str:
    urls = re.findall(r'https?://[^\s]+', text)
    if not urls:
        return text
    
    extracted_data = ""
    for url in urls:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                if any(ext in url.lower() for ext in ['.py', '.js', '.html', '.txt', '.json', '.sh', '.csv', 'raw', 'script']) or 'text' in content_type or 'json' in content_type:
                    page_content = response.text[:8000]
                else:
                    page_content = re.sub('<[^<]+?>', '', response.text)[:5000]
                    
                extracted_data += f"\n[ข้อมูลเชิงลึกจากลิงก์/สคริปต์ {url}]:\n{page_content}\n"
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            
    return text + "\n" + extracted_data

# 1. จัดการข้อความตัวหนังสือ (ตอบกลับเป็นข้อความเท่านั้น ไม่ส่งไฟล์เสียง)
@bot.message_handler(content_types=['text'])
def reply_text(message):
    raw_text = message.text
    text_input = extract_url_content(raw_text)
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemini-2.5-flash:free",
        "messages": [{"role": "user", "content": text_input}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        bot_reply = response.json()['choices'][0]['message']['content']
        bot.reply_to(message, bot_reply)
    except Exception as e:
        print(f"Text error: {e}")
        bot.reply_to(message, "ขออภัยจ้า สมองกลขัดข้องนิดหน่อยนะน้า")

# 2. จัดการข้อความเสียง (ตอบกลับเป็นข้อความ + ส่งไฟล์เสียงตอบกลับ)
@bot.message_handler(content_types=['voice'])
def reply_voice(message):
    bot.reply_to(message, "ได้รับเสียงแล้วครับน้า กำลังฟังและคิดคำตอบแป๊บน้า...")
    audio_path = None
    reply_audio_path = None
    try:
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        audio_data = requests.get(file_url).content

        audio_path = f"user_voice_{message.from_user.id}_{int(time.time())}.ogg"
        with open(audio_path, "wb") as f:
            f.write(audio_data)

        with open(audio_path, "rb") as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # ปรับปรุงโครงสร้าง Audio Payload ให้ถูกต้องตามข้อกำหนด OpenRouter
        payload = {
            "model": "google/gemini-2.5-flash:free",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "กรุณาฟังเสียงนี้แล้วตอบคำถามกลับเป็นภาษาไทยสั้น ๆ กระชับและเป็นกันเอง"},
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": encoded_audio,
                                "format": "ogg"
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        bot_reply = response.json()['choices'][0]['message']['content']

        # ส่งข้อความตัวหนังสือก่อน
        bot.reply_to(message, bot_reply)

        # สร้างไฟล์เสียง TTS และส่งกลับเฉพาะกรณีผู้ใช้ส่งเสียงมาเท่านั้น
        if bot_reply.strip():
            reply_audio_path = f"bot_reply_{message.from_user.id}_{int(time.time())}.mp3"
            tts_text = bot_reply[:500] if len(bot_reply) > 500 else bot_reply
            
            tts = gTTS(text=tts_text, lang='th')
            tts.save(reply_audio_path)
            time.sleep(0.5)

            if os.path.exists(reply_audio_path):
                with open(reply_audio_path, "rb") as audio_reply:
                    bot.send_voice(message.chat.id, audio_reply, reply_to_message_id=message.message_id)
    except Exception as e:
        print(f"Voice error: {e}")
        bot.reply_to(message, "ขออภัยครับน้า ระบบเสียงขัดข้องนิดหน่อย ลองใหม่อีกครั้งนะครับ")
    finally:
        for path in [audio_path, reply_audio_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass

bot.infinity_polling()
