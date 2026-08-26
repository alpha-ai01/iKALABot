import logging
import config
import os

_client = None

def get_client():
    global _client
    if _client is None:
        from google import genai
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client
def generate_gemini_response(prompt_data, is_vision=False, mime_type="image/jpeg", model_override=None):
    model = model_override or config.MODEL_CONFIG["GEMINI_CONFIG"]["primary"]

    from google.genai import types

    SYSTEM_INSTRUCTION = """คุณคือ iNummm_bot ผู้ช่วย AI บน Telegram ที่รองรับทั้งข้อความและเสียง
คุณสามารถรับข้อความ, ข้อความเสียง, ตอบเป็นข้อความ, และสร้างเสียงจากคำตอบได้
เมื่อผู้ใช้ส่งเสียง: ให้ถือว่าเสียงนั้นถูกแปลงเป็นข้อความเรียบร้อยแล้วและตอบเนื้อหาที่ผู้ใช้พูดมาโดยตรง
ตอบเฉพาะสิ่งที่ผู้ใช้ต้องการ ใช้ภาษาธรรมชาติ ไม่ต้องใช้ Markdown และไม่ต้องใส่เครื่องหมายเน้นข้อความ"""

    contents = []
    if is_vision:
        contents.append(types.Part.from_bytes(data=prompt_data, mime_type=mime_type))
        contents.append(types.Part.from_text(text="วิเคราะห์ภาพนี้อย่างละเอียด อธิบายข้อความ วัตถุ และข้อมูลสำคัญที่มองเห็น"))
    else:
        contents.append(types.Part.from_text(text=f"{SYSTEM_INSTRUCTION}\n\nคำถาม: {prompt_data}"))


    try:
        logging.info("[Gemini] Trying model: %s", model)
        from google.genai import types
        
        # Disable automatic function calling as per SDK recommendation for generate_content
        config_afc = types.AutomaticFunctionCallingConfig(disable=True)
        
        response = get_client().models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                automatic_function_calling=config_afc
            )
        )
        logging.info("[Gemini] Success")
        return (response.text or "").strip()
    except Exception as e:
        logging.error("[Gemini] Failed with model %s: %s", model, str(e)[:200])
        return ""

