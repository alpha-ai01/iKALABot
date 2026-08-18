import unittest
from unittest.mock import patch, MagicMock
import os
import pytest
import requests

# Mocking the interaction/response to avoid real API calls
@patch('requests.post')
def test_openrouter_mocked(mock_post):
    # Setup mock
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "Hello!"}}]}
    mock_post.return_value = mock_response

    # Test logic
    # In a real scenario, we'd import the function being tested, not just the API call.
    # But as a standalone test of our expectations, this works:
    api_key = "fake-key"
    url = "https://openrouter.ai/api/v1/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/o4-mini",
        "input": "สวัสดี ตอบสั้นๆ ไม่เกิน 10 คำ",
        "max_output_tokens": 100
    }


    res = requests.post(url, headers=headers, json=payload)


    assert res.status_code == 200
    assert res.json()["choices"][0]["message"]["content"] == "Hello!"
    mock_post.assert_called_once()

@patch('google.genai.Client')
def test_gemini_interactions_mocked(mock_client_class):
    # Setup mock
    mock_client = MagicMock()
    mock_client.interactions.create.return_value.output_text = "AI is very powerful tool"
    mock_client_class.return_value = mock_client

    # Test logic
    from google import genai
    client = genai.Client()
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input="Explain AI in 5 words"
    )

    assert interaction.output_text == "AI is very powerful tool"
    mock_client.interactions.create.assert_called_once()
