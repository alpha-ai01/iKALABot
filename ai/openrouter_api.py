import json
import logging
import requests
import config
from utils.logger import logger

def ask_openrouter(prompt: str) -> str:
    if not config.OPENROUTER_API_KEY:
        return "ยังไม่ได้ตั้งค่า OPENROUTER_API_KEY ในระบบ"
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        # เปลี่ยนรหัสโมเดลเป็นตัวที่ OpenRouter รองรับและเปิดให้ใช้ฟรี
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        
        if "choices" in res_data and len(res_data["choices"]) > 0:
            return res_data["choices"][0]["message"]["content"]
        elif "error" in res_data:
            logger.error(f"OpenRouter Error Payload: {res_data['error']}")
            return f"เกิดข้อผิดพลาดจาก AI: {res_data['error'].get('message', 'Unknown error')}"
        else:
            logger.error(f"Unexpected OpenRouter response: {res_data}")
            return "ไม่สามารถดึงคำตอบจาก AI ได้ในขณะนี้"
            
    except Exception as e:
        logger.error(f"Error calling OpenRouter: {e}")
        return f"เกิดข้อผิดพลาดในการเชื่อมต่อ AI: {e}"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_openrouter_response(prompt, is_x_search=False):
    """Call OpenRouter REST API using the OpenRouter endpoint described in the project docs.

    Uses config.OPENROUTER_MODEL by default,
    or config.DEFAULT_X_SEARCH_MODEL when is_x_search is True.
    Returns a safe stripped string on success or an empty string on failure.
    """
    model = config.DEFAULT_X_SEARCH_MODEL if is_x_search else config.OPENROUTER_MODEL

    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        logging.info("[OpenRouter] Trying model: %s", model)
        resp = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=15)
        if resp.status_code != 200:
            logging.error("[OpenRouter] Failed with model %s: %s", model, resp.status_code)
            return ""

        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            logging.error("[OpenRouter] No choices returned")
            return ""

        first = choices[0]
        message = first.get("message") or {}
        content = message.get("content")
        if not content:
            logging.error("[OpenRouter] No content returned")
            return ""

        logging.info("[OpenRouter] Success")
        return content.strip()

    except Exception as e:
        logging.error("[OpenRouter] API error: %s", str(e)[:200])
        return ""
