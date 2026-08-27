import pytest
from unittest.mock import MagicMock
from utils.tools import SearchRouter
from utils.response_manager import send_ai_response

def test_search_router_fallback():
    router = SearchRouter()
    result = router.search("test query")
    # Assert it returns a string and is either a result or the fallback message
    assert isinstance(result, str)
    assert result != ""


def test_response_manager_enforces_voice():
    # Mock bot and message
    bot = MagicMock()
    message = MagicMock()
    message.from_user.id = "user1"
    message.chat.id = "chat1"
    
    # This should call send_voice
    send_ai_response(bot, message, "Hello world")
    
    # Verify send_voice was called
    assert bot.send_voice.called
