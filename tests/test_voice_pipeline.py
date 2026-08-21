import pytest
from unittest.mock import MagicMock, patch
import config
import voice.speech_to_text

def test_speech_to_text_success():
    mock_audio = b"dummy_audio_data"
    
    with patch('voice.speech_to_text.get_client') as mock_get_client, \
         patch('config.VOICE_GEMINI_MODEL', 'gemini-3.1-flash-lite'):
        mock_response = MagicMock()
        mock_response.text = "Hello world"
        mock_get_client.return_value.models.generate_content.return_value = mock_response
        
        transcript = voice.speech_to_text.speech_to_text(mock_audio)
        assert transcript == "Hello world"

def test_speech_to_text_failure():
    mock_audio = b"dummy_audio_data"
    
    with patch('voice.speech_to_text.get_client') as mock_get_client, \
         patch('config.VOICE_GEMINI_MODEL', 'gemini-3.1-flash-lite'):
        mock_get_client.return_value.models.generate_content.side_effect = Exception("API Error")
        
        # New implementation returns empty string on failure instead of raising Exception
        transcript = voice.speech_to_text.speech_to_text(mock_audio)
        assert transcript == ""
