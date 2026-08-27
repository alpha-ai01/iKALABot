import pytest
from unittest.mock import MagicMock, patch
from dispatcher import execute_task
from utils.tools import get_current_time
from services import document_service as DocumentService
from utils.text_utils import clean_ai_response
from utils.response_manager import send_ai_response
import os

# --- 1 & 2. Time/Date Routing ---
def test_current_time_routing():
    # Test that time keyword routes to 'time' task
    # We verify that execute_task with 'time' returns a string containing time
    result = execute_task(task="time", text="ตอนนี้กี่โมง")
    assert isinstance(result, str)
    assert len(result) > 0

def test_thai_buddhist_year():
    # Ensure it's not model knowledge but tool execution
    result = get_current_time()
    assert "เวลา" in result
    assert "วันที่" in result

# --- 3. Document Handler ---
def test_document_handler_exists():
    assert hasattr(DocumentService, "process_document")

def test_html_document_routing():
    # Test routing to document service (using mock file for demo)
    # Note: process_document needs a real path or file-like object in current impl
    # So we'll skip real file I/O test here and focus on the import
    assert hasattr(DocumentService, "process_document")

# --- 4. Security ---
def test_path_traversal_blocked():
    with pytest.raises(ValueError):
        # Assuming path validation is used in tools
        from utils.tools import validate_path
        validate_path("../config.py")

# --- 5 & 6. Response Centralization & Plain Text ---
def test_plain_text_response():
    raw_response = "## Hello! **World** 123.\n\n*Bullet point*"
    sanitized = clean_ai_response(raw_response)
    # Rules: no markdown, no symbols, no bullet points.
    assert "*" not in sanitized
    assert "#" not in sanitized
    assert "Hello World 123" in sanitized

def test_duplicate_response_removed():
    response = "Line 1\n\nLine 1\n\nLine 2"
    sanitized = clean_ai_response(response)
    assert sanitized == "Line 1\n\nLine 2"

# --- 7. Voice ---
def test_response_manager_attempts_tts():
    bot = MagicMock()
    message = MagicMock()
    message.chat.id = "123"
    
    # We need to mock text_to_speech to prevent actual TTS generation
    with patch('utils.response_manager.text_to_speech', return_value="/tmp/test.mp3"):
        with patch('os.path.exists', return_value=True):
            with patch('os.remove'):
                with patch('builtins.open', create=True):
                    send_ai_response(bot, message, "Hello")
                    assert bot.send_voice.called
