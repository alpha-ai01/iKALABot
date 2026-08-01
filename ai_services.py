import requests
from config import OPENROUTER_API_KEY

def get_openrouter_response(prompt_text):
    """เรียกใช้งาน OpenRouter API"""
    if not OPENROUTER_API_KEY:
        return "กรุณาตั้งค่า OPENROUTER_API_KEY"
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "~openai/gpt-latest",
        "messages": [
            {"role": "user", "content": prompt_text}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=30)
        res_data = res.json()
        return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเรียก AI: {str(e)}"
