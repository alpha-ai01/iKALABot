import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

openrouter_stream_code = """
import requests
import json

def stream_openrouter_chat(api_key="<OPENROUTER_API_KEY>"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gemma-2-9b-it:free",
        "stream": True,
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload),
        stream=True
    )
    
    chunks = []
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            chunks.append(decoded_line)
            print(decoded_line)
            
    return chunks
"""

if "stream_openrouter_chat" not in content:
    content += "\n" + openrouter_stream_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน OpenRouter Streaming สำเร็จ ===")
