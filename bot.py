import os
import telebot
from flask import Flask, request
from groq import Groq

TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
client = Groq(api_key=GROQ_API)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_stream().read().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": message.text}],
            model="llama3-8b-8192",
        )
        bot.reply_to(message, chat_completion.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, "ขออภัยครับ เกิดข้อผิดพลาด")

if __name__ == "__main__":
    # การตั้งค่า Webhook (รันครั้งเดียว)
    bot.remove_webhook()
    bot.set_webhook(url=f"https://ikalabot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
