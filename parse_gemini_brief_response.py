import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

parse_brief_code = """
def parse_brief_ai_response():
    # Response object payload from gemini-3.6-flash
    response_payload = {
        "id": "v1_ChdpQUFvYXI...",
        "status": "completed",
        "usage": {
            "total_tokens": 197,
            "total_input_tokens": 8,
            "total_output_tokens": 12
        },
        "created": "2026-06-09T12:01:25Z",
        "steps": [
            {
                "type": "thought",
                "signature": "EvEFCu4FAQw..."
            },
            {
                "type": "model_output",
                "content": [
                    {
                        "type": "text",
                        "text": "AI learns patterns from data, then uses those patterns to make predictions or decisions on new data."
                    }
                ]
            }
        ],
        "object": "interaction",
        "model": "gemini-3.6-flash"
    }
    
    # Extract text from model_output step
    output_text = None
    for step in response_payload.get("steps", []):
        if step.get("type") == "model_output":
            for content_item in step.get("content", []):
                if content_item.get("type") == "text":
                    output_text = content_item.get("text")
                    break
    
    print("Extracted Text:", output_text)
    return output_text
"""

if "parse_brief_ai_response" not in content:
    content += "\n" + parse_brief_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มตัวจัดการ Parse JSON ผลลัพธ์อธิบาย AI สำเร็จ ===")
