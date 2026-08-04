import config
from ai.gemini_api import generate_gemini_response
from ai.openrouter_api import generate_openrouter_response

def route_request(prompt, provider="gemini", is_vision=False, is_x_search=False):
    """
    Router สำหรับสลับและเรียกใช้โมเดลให้ถูกต้องตามการใช้งาน
    """
    if provider == "gemini":
        return generate_gemini_response(prompt, is_vision=is_vision)
    elif provider == "openrouter":
        return generate_openrouter_response(prompt, is_x_search=is_x_search)
    else:
        # Fallback Default
        return generate_gemini_response(prompt, is_vision=False)
