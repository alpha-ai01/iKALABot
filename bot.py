import os
import telebot
from google import genai

# --------------------------------------------------
# 1. ตั้งค่า API Keys
# --------------------------------------------------
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# พจนานุกรมสำหรับจำ interaction_id
user_sessions = {}

# --------------------------------------------------
# 2. คำสั่ง /start และ /reset
# --------------------------------------------------
@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):
    user_id = message.chat.id
    user_sessions[user_id] = None
    bot.reply_to(message, "สวัสดีครับ! ผมคือ Telegram Bot ที่ขับเคลื่อนด้วย Gemini AI ✨\nส่งข้อความมาคุยกับผมได้เลยครับ! (พิมพ์ /reset เพื่อเริ่มคุยหัวข้อใหม่)")

# --------------------------------------------------
# 3. จัดการข้อความทั่วไป
# --------------------------------------------------
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text

    bot.send_chat_action(user_id, 'typing')

    try:
        prev_id = user_sessions.get(user_id)

        # เรียกใช้ Interactions API
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=user_input,
            previous_interaction_id=prev_id,
            system_instruction="คุณคือผู้ช่วย AI ที่เป็นมิตร ตอบคำถามอย่างสุภาพ ชัดเจน และกระชับ"
        )

        # บันทึก interaction_id และส่งคำตอบกลับ
        user_sessions[user_id] = interaction.id
        response_text = interaction.output_text

        bot.reply_to(message, response_text)

    except Exception as e:
        bot.reply_to(message, f"เกิดข้อผิดพลาด: {str(e)}")

# --------------------------------------------------
# 4. รัน Bot
# --------------------------------------------------
if __name__ == "__main__":
    print("Telegram Bot is running...")
    bot.infinity_polling()
