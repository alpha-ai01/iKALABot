import os
import pytest
from services.document_service import process_document
from utils.response_manager import send_ai_response
import tempfile
import time

def test_document_service_import():
    try:
        from services import document_service
        assert hasattr(document_service, 'process_document')
    except ImportError:
        pytest.fail("ImportError: cannot import document_service")

def test_document_processing_txt():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
        tmp.write("Hello World")
        tmp_path = tmp.name
    try:
        assert process_document(tmp_path) == "Hello World"
    finally:
        os.remove(tmp_path)

def test_document_processing_python():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write("print('Hello')")
        tmp_path = tmp.name
    try:
        assert process_document(tmp_path) == "print('Hello')"
    finally:
        os.remove(tmp_path)

def test_document_path_security():
    # Attempt to process a sensitive file
    # This should return "รูปแบบไฟล์ไม่รองรับ" because it's not a supported extension
    # or fail safely.
    result = process_document(".env")
    assert result == "รูปแบบไฟล์ไม่รองรับ"

def test_current_time_routing():
    from dispatcher import execute_task
    # "ตอนนี้กี่โมง" is a time keyword
    result = execute_task(task="time", text="ตอนนี้กี่โมง")
    assert "เวลา" in result
    assert "วันที่" in result

# Minimal test for response manager routing
def test_response_manager_enforces_voice():
    # This just checks if it imports and handles the call
    # The actual bot interaction needs full mocking
    from unittest.mock import MagicMock
    bot = MagicMock()
    message = MagicMock()
    # Should not raise exception
    send_ai_response(bot, message, "Hello")
    assert bot.reply_to.called
