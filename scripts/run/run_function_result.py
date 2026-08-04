import base64
import requests
from google import genai

try:
    client = genai.Client()

    # ดึง Step ที่มีการเรียกใช้ function call
    tool_call = next(s for s in interaction.steps if s.type == "function_call")

    # ดาวน์โหลดรูปภาพและแปลงเป็น Base64
    image_path = "https://goo.gle/instrument-img"
    image_bytes = requests.get(image_path).content
    base64_image_data = base64.b64encode(image_bytes).decode("utf-8")

    # ส่ง Function Result กลับไปยัง Gemini Interactions API
    final_interaction = client.interactions.create(
        model="gemini-2.5-flash",
        previous_interaction_id=interaction.id,
        input=[
            {
                "type": "function_result",
                "name": tool_call.name,
                "call_id": tool_call.id,
                "result": [
                    {"type": "text", "text": "instrument.jpg"},
                    {
                        "type": "image",
                        "mime_type": "image/jpeg",
                        "data": base64_image_data,
                    },
                ],
            }
        ],
    )

    print(final_interaction.output_text)

except NameError as e:
    print(f"[Error] ยังไม่ได้สร้างตัวแปร interaction: {e}")
except Exception as e:
    print(f"[Error]: {e}")
