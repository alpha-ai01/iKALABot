import pytest
import threading
from main import app, run_bot
import os
from unittest.mock import MagicMock, patch

def test_health_endpoint():
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["service"] == "iKALABot"

def test_root_endpoint():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert response.data.decode() == "iKALABot is running live!"

def test_no_secrets_in_health():
    client = app.test_client()
    response = client.get('/health')
    assert "TELEGRAM_BOT_TOKEN" not in str(response.data)
    assert "OPENROUTER_API_KEY" not in str(response.data)
    assert "GEMINI_API_KEY" not in str(response.data)

@patch('telebot.TeleBot')
def test_polling_starts_once(mock_telebot):
    # This just tests if the function runs, not necessarily the polling mechanism itself
    # But verifies it initializes correctly
    token = "dummy_token"
    # We use a mock that raises an exception to stop polling immediately, to avoid infinite loop
    mock_bot = mock_telebot.return_value
    mock_bot.infinity_polling.side_effect = Exception("Stop polling")

    try:
        run_bot(token)
    except Exception as e:
        assert str(e) == "Stop polling"

    mock_bot.remove_webhook.assert_called_once()
    mock_bot.infinity_polling.assert_called_once()
