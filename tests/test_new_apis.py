import os
import requests
from google import genai

# ==========================================
# 1. ทดสอบ OpenRouter Responses API (สเปกใหม่)
# ==========================================
def test_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("[-] Skip OpenRouter: ไม่พบ OPENROUTER_API_KEY")
        return

    print("[+] Testing OpenRouter Responses API...")
    url = "https://openrouter.ai/api/v1/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/o4-mini",
        "input": "สวัสดี ตอบสั้นๆ ไม่เกิน 10 คำ",
        "max_output_tokens": 100
    }
    
    try:
        res = requests.post(url, headers=headers, json=payload)
        print("OpenRouter Response Status:", res.status_code)
        print("Result:", res.json())
    except Exception as e:
        print("OpenRouter Error:", e)

# ==========================================
# 2. ทดสอบ Gemini Interactions API (สเปกใหม่)
# ==========================================
def test_gemini_interactions():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[-] Skip Gemini: ไม่พบ GEMINI_API_KEY")
        return

    print("\n[+] Testing Gemini Interactions API...")
    try:
        client = genai.Client()
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input="Explain AI in 5 words"
        )
        print("Gemini Result:", interaction.output_text)
    except Exception as e:
        print("Gemini Error:", e)

if __name__ == "__main__":
    test_openrouter()
    test_gemini_interactions()
