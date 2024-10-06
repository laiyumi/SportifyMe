import os
import json
import replicate

# 从 config.json 中加载配置
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# 获取 API Key
api_token = config.get("REPLICATE_API_TOKEN")
if not api_token:
    raise ValueError("API token is missing in config.json!")

# 设置 Replicate API token 作为环境变量
os.environ["REPLICATE_API_TOKEN"] = api_token

import os
import replicate

def perform_inference(user_health_data):
    """
    Uses Replicate API to infer the current state, gap, and history improvement based on user health data.

    Args:
        user_health_data (dict): Dictionary containing the user's health data (e.g., heart_rate, body_fat_percentage, flexibility_score).

    Returns:
        dict: Contains prediction results for "recommendation_gap", "recommendation_currentState", and "history_improvement".
    """
    # Three separate prompts for each type of response
    prompt_current_state = (
        f"Based on the Ministry of Health’s 2024 health standards and your current fitness data (heart rate: {user_health_data['heart_rate']}, "
        f"body fat: {user_health_data['body_fat_percentage']}, flexibility score: {user_health_data['flexibility_score']}), explain the user's "
        "current fitness level. Also, include a lighthearted fitness joke or 'legend' to make the response fun. Keep it within 300 words."
    )

    prompt_gap = (
        f"Assume the user's target activity is climbing a 3000-meter peak. Based on the user's fitness data (heart rate: {user_health_data['heart_rate']}, "
        f"body fat: {user_health_data['body_fat_percentage']}, flexibility score: {user_health_data['flexibility_score']}), provide suggestions on the gap between "
        "their current fitness level and the target activity. Suggestions should cover: 1. daily exercise, 2. dietary structure, and 3. skill training. End with an encouraging message like “You’ve got this, keep pushing!” Keep it within 300 words."
    )

    prompt_history_improvement = (
        f"Please check the user's historical health data, combining their current data (heart rate: {user_health_data['heart_rate']}, body fat: {user_health_data['body_fat_percentage']}, "
        f"flexibility score: {user_health_data['flexibility_score']}). Analyze the user's improvements and quantify the progress if possible. Conclude with a scientific statement like "
        "“Studies show that consistent exercise improves overall health.” Keep it within 300 words."
    )

    # One function to handle all prompts and return the responses
    def get_response(prompt):
        response = ""
        try:
            for event in replicate.stream(
                "meta/meta-llama-3-70b-instruct",
                input={
                    "top_p": 0.9,
                    "prompt": prompt,
                    "max_tokens": 512,
                    "min_tokens": 0,
                    "temperature": 0.6,
                    "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                    "presence_penalty": 1.15
                }
            ):
                response += str(event)
        except Exception as e:
            print(f"Error during inference: {e}")
            return "Error during inference"
        
        return response.strip()

    # Get the responses for each prompt
    recommendation_currentState = get_response(prompt_current_state)
    recommendation_gap = get_response(prompt_gap)
    
    # Check if historical data exists before calling the history improvement prompt
    if "historical_data" in user_health_data:
        history_improvement = get_response(prompt_history_improvement)
    else:
        history_improvement = "No history available, Get back one month later, grade your progress!!!"

    # Return the final prediction
    return {
        "recommendation_currentState": recommendation_currentState,
        "recommendation_gap": recommendation_gap,
        "history_improvement": history_improvement
    }

"""
# Example usage
user_health_data = {
    "heart_rate": 75,
    "body_fat_percentage": 20.5,
    "flexibility_score": 7,
    "historical_data": True  # Add this if historical data exists, or remove it if there's none
}

result = perform_inference(user_health_data)

# Print each part of the result separately
print("Current State Recommendation:\n", result.get("recommendation_currentState", "No data available"))
print("\nGap Recommendation:\n", result.get("recommendation_gap", "No data available"))
print("\nHistory Improvement Recommendation:\n", result.get("history_improvement", "No data available"))
"""
