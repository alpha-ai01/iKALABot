import pytest
from unittest.mock import MagicMock, patch
import config
import voice.speech_to_text

def test_audio_model_config_exists():
    assert config.VOICE_GEMINI_MODEL == config.MODEL_CONFIG["gemini"]["audio"]

def test_speech_to_text_success():
    mock_audio = b"dummy_audio_data"
    mock_mime = "audio/ogg"
    
    with patch('voice.speech_to_text.get_client') as mock_get_client:
        mock_response = MagicMock()
        mock_response.text = "Hello world"
        mock_get_client.return_value.models.generate_content.return_value = mock_response
        
        transcript = voice.speech_to_text.speech_to_text(mock_audio, mime_type=mock_mime)
        
        # Verify call to generate_content
        mock_get_client.return_value.models.generate_content.assert_called_once()
        args, kwargs = mock_get_client.return_value.models.generate_content.call_args
        assert kwargs['model'] == config.VOICE_GEMINI_MODEL
        # Check if mime_type was passed in the contents
        assert kwargs['contents'][1].inline_data.mime_type == mock_mime
        
        assert transcript == "Hello world"

def test_speech_to_text_failure():
    mock_audio = b"dummy_audio_data"
    
    with patch('voice.speech_to_text.get_client') as mock_get_client:
        mock_get_client.return_value.models.generate_content.side_effect = Exception("API Error")
        
        transcript = voice.speech_to_text.speech_to_text(mock_audio)
        assert transcript == ""
