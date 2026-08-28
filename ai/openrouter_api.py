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
        # ใช้รหัสโมเดลจาก config
        "model": config.MODEL_CONFIG["OPENROUTER"]["primary"],
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        res_data = response.json()
        
        if "choices" in res_data and len(res_data["choices"]) > 0:
            return res_data["choices"][0]["message"]["content"]
        elif "error" in res_data:
            logger.error(f"OpenRouter Error Payload: {res_data['error']}")
            return "เกิดข้อผิดพลาดจากระบบ AI กรุณาลองใหม่อีกครั้ง"
        else:
            logger.error(f"Unexpected OpenRouter response: {res_data}")
            return "ไม่สามารถดึงคำตอบจาก AI ได้ในขณะนี้"
            
    except Exception as e:
        logger.error(f"Error calling OpenRouter: {e}")
        return "เกิดข้อผิดพลาดในการเชื่อมต่อ AI กรุณาลองใหม่อีกครั้ง"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_openrouter_response(prompt, is_reasoning=False, stream=False):
    """Call OpenRouter REST API.
    
    If is_reasoning is True, uses the reasoning model and enables reasoning in extra_body.
    Returns response content string.
    """
    if is_reasoning:
        model = config.MODEL_CONFIG["openrouter"]["reasoning"]
    else:
        model = config.MODEL_CONFIG["openrouter"]["primary"]

    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": stream
    }
    
    if is_reasoning:
        payload["extra_body"] = {"reasoning": {"enabled": True}}

    try:
        logging.info("[OpenRouter] Trying model: %s (Reasoning: %s)", model, is_reasoning)
        resp = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=30)
        if resp.status_code != 200:
            logging.error("[OpenRouter] Failed with model %s: %s", model, resp.status_code)
            return ""

        # Simplified for now, assuming no stream for simplicity unless explicitly needed by wrapper
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
