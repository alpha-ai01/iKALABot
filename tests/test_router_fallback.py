import unittest
from unittest.mock import patch
from ai.router import route_request
import config

class TestRouterFallback(unittest.TestCase):

    @patch('ai.gemini_api.generate_gemini_response')
    @patch('ai.gateway.requests.post')
    def test_fallback_flow(self, mock_requests, mock_gemini):
        # Scenario 1: OpenRouter fails -> Gemini succeeds
        
        # Mock OpenRouter failure (e.g., status 404 or empty response)
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404
        mock_requests.return_value = mock_response
        
        mock_gemini.return_value = "Gemini Success"
        
        response = route_request("Test prompt")
        self.assertEqual(response, "Gemini Success")
        
        # Scenario 2: OpenRouter succeeds
        
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "OpenRouter Success"}}]}
        
        response = route_request("Test prompt")
        self.assertEqual(response, "OpenRouter Success")

if __name__ == '__main__':
    unittest.main()
