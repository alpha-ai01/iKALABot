import os
import telebot
from groq import Groq

# 1. ดึงค่า Key จาก Environment Variables (เราจะไปตั้งค่าใน Render ทีหลัง)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# 2. ตั้งค่าการเชื่อมต่อ Bot และ Groq
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# 3. ฟังก์ชันต้อนรับเมื่อพิมพ์ /start หรือ /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = "สวัสดีครับ! ผมคือ AI Bot ที่ขับเคลื่อนด้วยความเร็วของ Groq พิมพ์ข้อความมาคุยกันได้เลยครับ"
    bot.reply_to(message, welcome_text)

# 4. ฟังก์ชันรับข้อความและส่งไปให้ Groq ประมวลผล
@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        # เรียกใช้งาน Groq API (ใช้โมเดล Llama 3)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message.text,
                }
            ],
            model="llama3-8b-8192", 
        )
        
        # ดึงข้อความตอบกลับและส่งกลับไปที่ Telegram
        reply = chat_completion.choices[0].message.content
        bot.reply_to(message, reply)
        
    except Exception as e:
        bot.reply_to(message, "ขออภัยครับ เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI")
        print(f"Error: {e}")

# 5. สั่งให้บอทรันทำงานตลอดเวลา
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
