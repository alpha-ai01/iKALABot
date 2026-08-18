import pytest
from unittest.mock import MagicMock, patch
import os

# Mock dependencies
with patch('google.genai.Client'), patch('config.DEFAULT_GEMINI_MODEL', 'gemini-1.5-flash'):
    from voice.speech_to_text import speech_to_text

def test_speech_to_text_success():
    mock_audio = b"dummy_audio_data"
    
    with patch('voice.speech_to_text.get_client') as mock_get_client:
        mock_response = MagicMock()
        mock_response.text = "Hello world"
        mock_get_client.return_value.models.generate_content.return_value = mock_response
        
        transcript = speech_to_text(mock_audio)
        assert transcript == "Hello world"

def test_speech_to_text_failure():
    mock_audio = b"dummy_audio_data"
    
    with patch('voice.speech_to_text.get_client') as mock_get_client:
        mock_get_client.return_value.models.generate_content.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            speech_to_text(mock_audio)
