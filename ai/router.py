from ai.gemini_api import generate_gemini_response
from ai.openrouter_api import generate_openrouter_response

def route_request(
    prompt,
    provider='auto',
    is_vision=False,
    is_x_search=False,
):
    if provider == 'gemini':
        return generate_gemini_response(
            prompt,
            is_vision=is_vision
        )

    if provider == 'openrouter':
        return generate_openrouter_response(
            prompt,
            is_x_search=is_x_search
        )

    try:
        return generate_gemini_response(
            prompt,
            is_vision=is_vision
        )
    except Exception as e:
        print(f'[Router] Gemini failed: {e}')
        return generate_openrouter_response(
            prompt,
            is_x_search=is_x_search
        )
