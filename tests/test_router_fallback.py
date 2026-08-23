import unittest
from unittest.mock import patch
from ai.router import route_request
import config

class TestRouterFallback(unittest.TestCase):

    @patch('ai.router.generate_gemini_response')
    @patch('ai.router.generate_openrouter_response')
    def test_fallback_flow(self, mock_openrouter, mock_gemini):
        # Scenario 1: Gemini (primary) fails -> OpenRouter succeeds
        
        # Define mock side effects that change per call
        def gemini_side_effect_1(*args, **kwargs):
            if kwargs.get('model_override') == config.MODEL_CONFIG["GOOGLE"]["primary"]:
                return ""
            return ""
        
        mock_gemini.side_effect = gemini_side_effect_1
        mock_openrouter.return_value = "OpenRouter Success"
        
        response = route_request("Test prompt")
        self.assertEqual(response, "OpenRouter Success")
        
        # Scenario 2: Gemini (primary) fails -> OpenRouter fails -> Gemini (lite) succeeds
        
        def gemini_side_effect_2(*args, **kwargs):
            if kwargs.get('model_override') == config.MODEL_CONFIG["GOOGLE"]["primary"]:
                return ""
            if kwargs.get('model_override') == config.MODEL_CONFIG["GOOGLE"]["fallback"]:
                return "Gemini Lite Success"
            return ""
            
        mock_gemini.side_effect = gemini_side_effect_2
        mock_openrouter.return_value = ""
        
        response = route_request("Test prompt")
        self.assertEqual(response, "Gemini Lite Success")

if __name__ == '__main__':
    unittest.main()
