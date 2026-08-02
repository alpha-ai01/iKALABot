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
        "model": "google/gemini-2.0-flash-exp:free",
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
