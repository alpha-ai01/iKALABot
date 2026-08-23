import unittest
from unittest.mock import patch
from ai.router import route_request

class TestRouterFallback(unittest.TestCase):

    @patch('ai.gateway.AIGateway.call_ai')
    def test_routing_flow(self, mock_call_ai):
        # Scenario 1: AIGateway succeeds
        mock_call_ai.return_value = "Success"
        
        response = route_request("Test prompt")
        self.assertEqual(response, "Success")
        
        # Scenario 2: AIGateway fails
        mock_call_ai.return_value = "Error: some error"
        
        response = route_request("Test prompt")
        self.assertIn("ขออภัย", response)

if __name__ == '__main__':
    unittest.main()
