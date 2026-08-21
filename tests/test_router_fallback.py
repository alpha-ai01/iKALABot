import unittest
from unittest.mock import patch
from ai.router import route_request
import config

class TestRouterFallback(unittest.TestCase):

    @patch('ai.router.generate_gemini_response')
    @patch('ai.router.generate_openrouter_response')
    def test_fallback_flow(self, mock_openrouter, mock_gemini):
        # Mocking generate_gemini_response to handle different calls based on model_override
        def gemini_side_effect(prompt, is_vision=False, mime_type="image/jpeg", model_override=None):
            if model_override == config.GEMINI_MODEL:
                return "" # Fail first Gemini
            if model_override == config.GEMINI_FALLBACK_MODEL:
                return "Gemini Lite Success"
            return ""

        mock_gemini.side_effect = gemini_side_effect
        
        # Scenario 1: Gemini (primary) fails -> OpenRouter succeeds
        mock_openrouter.return_value = "OpenRouter Success"
        response = route_request("Test prompt")
        self.assertEqual(response, "OpenRouter Success")
        
        # Scenario 2: Gemini (primary) fails -> OpenRouter fails -> Gemini (lite) succeeds
        mock_openrouter.return_value = ""
        response = route_request("Test prompt")
        self.assertEqual(response, "Gemini Lite Success")

if __name__ == '__main__':
    unittest.main()
