import os
import telebot
from groq import Groq

# ดึงค่าจาก Environment Variable ที่เราตั้งไว้ใน Render
API_TOKEN = os.environ.get('API_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# --- ส่วน Logic การคุยกับ AI (เอาโค้ดเดิมของคุณมาไว้ตรงนี้) ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama-3.1-8b-instant", # หรือชื่อ Model เดิมที่คุณใช้
        )
        response_text = chat_completion.choices[0].message.content
        bot.reply_to(message, response_text)
    except Exception as e:
        bot.reply_to(message, "ขออภัยครับ เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI")
        print(f"DEBUG_ERROR: {e}")

# --- ส่วน Webhook (ไม่ต้องแก้ไข) ---
@server.route('/' + API_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{API_TOKEN}")
    return "Webhook set!", 200

if __name__ == "__main__":
    # รันบนพอร์ต 10000 ตามที่ Render กำหนด
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
