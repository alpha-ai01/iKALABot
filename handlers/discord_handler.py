import discord
from discord.ext import commands
import logging
import os
import asyncio
from dispatcher import execute_task
from ai.gemini_api import generate_gemini_response
from voice.text_to_speech import text_to_speech
from utils.text_utils import clean_ai_response
import config

def run_discord_bot(token):
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='/', intents=intents)

    @bot.event
    async def on_ready():
        logging.info(f'Discord Bot logged in as {bot.user.name} (ID: {bot.user.id})')
        print(f'Discord Bot logged in as {bot.user.name}')

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        # 1. Handle Photo/Image Attachment
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['jpg', 'jpeg', 'png', 'webp']):
                    await handle_photo(message, attachment)
                    return # Process only the first image for now, matching Telegram behavior

        # 2. Handle Text Message
        if message.content:
            await handle_text(message)

    async def handle_text(message):
        text = message.content
        
        # Replicate classification logic from Telegram
        task = "chat"
        kwargs = {}

        if any(keyword in text.lower() for keyword in ["กี่โมง", "วันที่", "time", "date"]):
            task = "time"
        elif "ค้นหา" in text:
            task = "search"

        try:
            async with message.channel.typing():
                response = execute_task(task, text=text, **kwargs)
                if not response:
                    response = "ขออภัยครับ ไม่เข้าใจคำสั่ง"
                
                clean_res = clean_ai_response(str(response))
                await message.reply(clean_res)
        except Exception as e:
            logging.exception("DISCORD_TEXT_FAILED")
            await message.reply(f"เกิดข้อผิดพลาด: {str(e)}")

    async def handle_photo(message, attachment):
        logging.info(f"DISCORD_PHOTO_RECEIVED: from={message.author}")
        try:
            async with message.channel.typing():
                # Download the image asynchronously using discord.py's read method
                downloaded_file = await attachment.read()
                
                logging.info("DISCORD_VISION_START")
                # mime_type logic
                mime_type = "image/jpeg"
                if attachment.filename.lower().endswith('png'):
                    mime_type = "image/png"
                elif attachment.filename.lower().endswith('webp'):
                    mime_type = "image/webp"
                
                ai_response = generate_gemini_response(downloaded_file, is_vision=True, mime_type=mime_type)
                
                if not ai_response:
                    logging.info("DISCORD_VISION_EMPTY")
                    await message.reply("ขออภัยครับ ไม่สามารถวิเคราะห์ภาพนี้ได้")
                    return
                
                logging.info("DISCORD_VISION_OK")
                clean_res = clean_ai_response(str(ai_response))
                
                # Send text response
                await message.reply(clean_res)
                logging.info("DISCORD_PHOTO_REPLY_TEXT_OK")

                # TTS and send voice
                logging.info("DISCORD_TTS_START")
                audio_path = text_to_speech(clean_res)
                
                if audio_path:
                    logging.info("DISCORD_SENDING_VOICE")
                    try:
                        file = discord.File(audio_path, filename="voice_response.mp3")
                        await message.channel.send(file=file)
                        logging.info("DISCORD_VOICE_SENT_OK")
                    finally:
                        # Cleanup
                        if os.path.exists(audio_path):
                            os.remove(audio_path)
                            logging.info("DISCORD_TEMP_VOICE_REMOVED")
                else:
                    logging.info("DISCORD_TTS_FAILED_FALLBACK")
                    
        except Exception as e:
            logging.exception("DISCORD_VISION_FAILED")
            await message.reply(f"เกิดข้อผิดพลาดในการรับภาพ: เกิดปัญหาภายในระบบ")

    # Start the bot
    bot.run(token)
