import unittest
from unittest.mock import patch, MagicMock
from inference_module import perform_inference

class TestInferenceModule(unittest.TestCase):
    
    @patch('replicate.stream')
    def test_happy_path_printing(self, mock_replicate_stream):
        """
        Test the happy path: whether the results are printed correctly and API returns valid results.
        """
        # Mocking the response from Replicate API
        mock_replicate_stream.return_value = iter([
            "Based on the Ministry of Health’s 2024 standards...",
            "Here is a fun joke about fitness...",
            "For the target activity of climbing 3000 meters...",
            "Based on your historical health data, you've improved..."
        ])

        # Sample user health data for the test
        user_health_data = {
            "heart_rate": 72,
            "body_fat_percentage": 18.5,
            "flexibility_score": 8,
            "historical_data": True
        }

        # Run the inference
        result = perform_inference(user_health_data)

        # Assert the results are correctly populated
        self.assertIn("recommendation_currentState", result)
        self.assertIn("recommendation_gap", result)
        self.assertIn("history_improvement", result)
        
        # Print results (this would be the same as what the user wants)
        print("Current State Recommendation:\n", result.get("recommendation_currentState"))
        print("\nGap Recommendation:\n", result.get("recommendation_gap"))
        print("\nHistory Improvement Recommendation:\n", result.get("history_improvement"))

    @patch('replicate.stream')
    def test_correct_database_retrieval(self, mock_replicate_stream):
        """
        Test whether the system correctly retrieves data from the database (simulated using mock).
        """
        # Mock API response
        mock_replicate_stream.return_value = iter([
            "Current state level is moderate...",
            "Gap between current fitness and climbing 3000m is...",
            "Historical improvement detected..."
        ])

        # Simulated user health data retrieved from the database
        user_health_data = {
            "heart_rate": 80,
            "body_fat_percentage": 22.0,
            "flexibility_score": 6,
            "historical_data": True
        }

        # Run inference and check results
        result = perform_inference(user_health_data)
        
        # Check that all keys are present in the result
        self.assertIn("recommendation_currentState", result)
        self.assertIn("recommendation_gap", result)
        self.assertIn("history_improvement", result)

    @patch('replicate.stream')
    def test_final_return_values(self, mock_replicate_stream):
        """
        Test the final return values to ensure the structure is correct and responses are handled accurately.
        """
        # Mocking responses for three different cases
        mock_replicate_stream.side_effect = [
            iter(["Your current state is good..."]),  # current state
            iter(["You need to improve in these areas..."]),  # gap recommendation
            iter(["Your improvement history shows..."])  # history improvement
        ]

        user_health_data = {
            "heart_rate": 75,
            "body_fat_percentage": 20.0,
            "flexibility_score": 7,
            "historical_data": True
        }

        # Run inference
        result = perform_inference(user_health_data)

        # Check if the returned values match the expected structure
        self.assertEqual(result["recommendation_currentState"], "Your current state is good...")
        self.assertEqual(result["recommendation_gap"], "You need to improve in these areas...")
        self.assertEqual(result["history_improvement"], "Your improvement history shows...")

        # Also ensure no data is missing
        self.assertNotEqual(result["recommendation_currentState"], "")
        self.assertNotEqual(result["recommendation_gap"], "")
        self.assertNotEqual(result["history_improvement"], "")

if __name__ == '__main__':
    unittest.main()
