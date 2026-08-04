import os
import config

def get_gemini_model_name(is_vision=False):
    if is_vision:
        return config.DEFAULT_GEMINI_VISION_MODEL
    return config.DEFAULT_GEMINI_MODEL

def generate_gemini_response(prompt, is_vision=False):
    model_name = get_gemini_model_name(is_vision)
    # คงโครงสร้างเดิมของการจัดการ API Call
    return f"Response using Gemini Model: {model_name}"
