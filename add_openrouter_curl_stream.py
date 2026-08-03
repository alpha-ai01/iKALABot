import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

curl_stream_code = """
import requests
import json

def run_openrouter_curl_stream(api_key="<OPENROUTER_API_KEY>"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
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
    
    stream_output = []
    for line in response.iter_lines():
        if line:
            decoded = line.decode('utf-8')
            stream_output.append(decoded)
            print(decoded)
            
    return stream_output
"""

if "run_openrouter_curl_stream" not in content:
    content += "\n" + curl_stream_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน OpenRouter cURL Streaming สำเร็จ ===")
