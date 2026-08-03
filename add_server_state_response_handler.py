import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

response_handler_code = """
def handle_paw_calculation_response():
    # Response JSON data from server-side state conversation
    response_data = {
        "id": "v2_Chd...",
        "status": "completed",
        "usage": {
            "total_tokens": 240,
            "total_input_tokens": 60,
            "total_output_tokens": 20
        },
        "steps": [
            {
                "type": "model_output",
                "content": [
                    {
                        "type": "text",
                        "text": "There are 8 paws in your house. 2 dogs \\u00d7 4 paws = 8 paws."
                    }
                ]
            }
        ],
        "object": "interaction",
        "model": "gemini-3.6-flash"
    }
    
    text_output = response_data["steps"][0]["content"][0]["text"]
    print("Parsed Output:", text_output)
    return text_output
"""

if "handle_paw_calculation_response" not in content:
    content += "\n" + response_handler_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มตัวจัดการผลลัพธ์ Server-side state สำเร็จ ===")
