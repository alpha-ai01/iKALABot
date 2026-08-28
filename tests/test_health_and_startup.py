import pytest
import threading
import main
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
    main.polling_started = False # Reset for test
    token = "dummy_token"
    mock_bot = mock_telebot.return_value
    mock_bot.infinity_polling.side_effect = Exception("Stop polling")

    try:
        run_bot(token)
    except Exception:
        pass

    mock_bot.remove_webhook.assert_called_once()
    mock_bot.infinity_polling.assert_called_once()

    # Try starting again
    run_bot(token)
    # The second call should have returned early due to polling_started = True
    assert mock_bot.infinity_polling.call_count == 1

@patch('telebot.TeleBot')
def test_409_conflict_handling(mock_telebot):
    main.polling_started = False # Reset
    token = "dummy_token"
    mock_bot = mock_telebot.return_value
    mock_bot.infinity_polling.side_effect = Exception("409 Conflict")

    # This should not raise or retry infinitely
    run_bot(token)
    
    assert mock_bot.infinity_polling.call_count == 1
    main.polling_started = False # Reset for other tests
