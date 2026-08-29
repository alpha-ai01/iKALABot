import unittest
from unittest.mock import patch, MagicMock
from ai.openrouter_client import OpenRouterClient
import requests

class TestOpenRouterClient(unittest.TestCase):
    @patch('ai.openrouter_client.requests.post')
    def test_call_model_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Hello!"}}]}
        mock_post.return_value = mock_response
        result = OpenRouterClient.call_model("test-model", {"prompt": "hi"})
        self.assertEqual(result, "Hello!")

    @patch('ai.openrouter_client.requests.post')
    def test_call_model_401(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response
        result = OpenRouterClient.call_model("test-model", {"prompt": "hi"})
        self.assertIsNone(result)

    @patch('ai.openrouter_client.requests.post')
    def test_call_model_403(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
        mock_post.return_value = mock_response
        result = OpenRouterClient.call_model("test-model", {"prompt": "hi"})
        self.assertIsNone(result)
        # Should be pruned eventually
        
    @patch('ai.openrouter_client.requests.post')
    def test_call_model_404(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_post.return_value = mock_response
        result = OpenRouterClient.call_model("test-model", {"prompt": "hi"})
        self.assertIsNone(result)

    @patch('ai.openrouter_client.requests.post')
    def test_call_model_429(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_post.return_value = mock_response
        result = OpenRouterClient.call_model("test-model", {"prompt": "hi"})
        self.assertIsNone(result)

    @patch('ai.openrouter_client.requests.post')
    def test_call_model_500(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
        mock_post.return_value = mock_response
        result = OpenRouterClient.call_model("test-model", {"prompt": "hi"})
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
