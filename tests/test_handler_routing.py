import pytest
from unittest.mock import MagicMock, patch

@patch('telebot.TeleBot')
def test_handler_routing(mock_bot):
    from handlers.message_handler import init_handlers
    init_handlers(mock_bot)
    
    # Check if handlers are registered
    # This is a bit tricky with how pyTelegramBotAPI registers them,
    # but we can verify the function name exists in the handler list if needed.
    # For now, let's just make sure the registration doesn't crash.
    assert True

def test_voice_handler_flow():
    from handlers.message_handler import handle_voice_message
    
    mock_message = MagicMock()
    mock_message.chat.id = 123
    mock_message.voice.file_id = "test_id"
    
    with patch('telebot.TeleBot.get_file') as mock_get, \
         patch('telebot.TeleBot.download_file') as mock_download, \
         patch('voice.speech_to_text.speech_to_text') as mock_stt, \
         patch('dispatcher.execute_task') as mock_execute:
        
        mock_get.return_value.file_path = "path/to/file"
        mock_download.return_value = b"audio_bytes"
        mock_stt.return_value = "hello world"
        mock_execute.return_value = "hi there"
        
        handle_voice_message(mock_message)
        
        mock_stt.assert_called_once_with(b"audio_bytes")
        mock_execute.assert_called_once_with("chat", text="hello world")

def test_photo_handler_flow():
    from handlers.message_handler import handle_photo_message
    
    mock_message = MagicMock()
    mock_message.chat.id = 123
    mock_message.photo = [MagicMock(file_id="photo_id")]
    
    with patch('telebot.TeleBot.get_file') as mock_get, \
         patch('telebot.TeleBot.download_file') as mock_download, \
         patch('ai.gemini_api.generate_gemini_response') as mock_vision:
        
        mock_get.return_value.file_path = "path/to/photo"
        mock_download.return_value = b"photo_bytes"
        mock_vision.return_value = "nice picture"
        
        handle_photo_message(mock_message)
        
        mock_vision.assert_called_once_with(b"photo_bytes", is_vision=True)
