from telebot import TeleBot
from ai_services import get_openrouter_response

def register_bot_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "สวัสดีครับ บอทพร้อมใช้งานแล้ว!")

    @bot.message_handler(func=lambda message: True)
    def handle_text_messages(message):
        bot.send_chat_action(message.chat.id, 'typing')
        ai_reply = get_openrouter_response(message.text)
        bot.reply_to(message, ai_reply)
