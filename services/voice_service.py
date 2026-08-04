def process_voice_message(bot, message):
    try:
        file_id = message.voice.file_id if message.voice else message.audio.file_id

        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)

        return {
            "status": "downloaded",
            "file_path": file_info.file_path,
            "data": downloaded,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
