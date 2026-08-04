import os
import config

def get_openrouter_model_name(is_x_search=False):
    if is_x_search:
        return config.DEFAULT_X_SEARCH_MODEL
    return config.DEFAULT_OPENROUTER_MODEL

def generate_openrouter_response(prompt, is_x_search=False):
    model_name = get_openrouter_model_name(is_x_search)
    # คงโครงสร้างเดิมของการเรียก OpenRouter
    return f"Response using OpenRouter Model: {model_name}"
