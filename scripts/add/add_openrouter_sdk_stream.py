import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

sdk_stream_code = """
# Python equivalent of the OpenRouter SDK streaming snippet with reasoning tokens extraction
import requests
import json

def run_openrouter_sdk_style_stream(api_key="<OPENROUTER_API_KEY>"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemma-2-9b-it:free",
        "messages": [
            {
                "role": "user",
                "content": "How many r's are in the word 'strawberry'?"
            }
        ],
        "stream": True,
        "reasoning": {"enabled": True}
    }
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload),
        stream=True
    )
    
    full_response = ""
    reasoning_tokens = None
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith("data: "):
                data_str = line_str[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        content_piece = delta.get("content")
                        if content_piece:
                            full_response += content_piece
                            print(content_piece, end="", flush=True)
                            
                    if "usage" in chunk and chunk["usage"]:
                        details = chunk["usage"].get("completion_tokens_details")
                        if details:
                            reasoning_tokens = details.get("reasoning_tokens")
                except json.JSONDecodeError:
                    pass
                    
    if reasoning_tokens is not None:
        print(f"\\nReasoning tokens: {reasoning_tokens}")
        
    return {"response": full_response, "reasoning_tokens": reasoning_tokens}
"""

if "run_openrouter_sdk_style_stream" not in content:
    content += "\n" + sdk_stream_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน OpenRouter SDK-Style Streaming สำเร็จ ===")
