import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

js_reasoning_code = """
# Equivalent Python implementation of the OpenRouter multi-turn reasoning flow provided in JavaScript
import requests
import json

def run_js_style_openrouter_reasoning(api_key="<OPENROUTER_API_KEY>"):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # First API call with reasoning enabled
    payload1 = {
        "model": "gemma-2-9b-it:free",
        "messages": [
            {
                "role": "user",
                "content": "How many r's are in the word 'strawberry'?"
            }
        ],
        "reasoning": {"enabled": True}
    }
    
    resp1 = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload1)
    )
    
    result1 = resp1.json()
    if 'choices' not in result1:
        return result1
        
    assistant_msg = result1['choices'][0]['message']
    
    # Preserve assistant message with reasoning_details
    messages = [
        {
            "role": "user",
            "content": "How many r's are in the word 'strawberry'?"
        },
        {
            "role": "assistant",
            "content": assistant_msg.get('content'),
            "reasoning_details": assistant_msg.get('reasoning_details')
        },
        {
            "role": "user",
            "content": "Are you sure? Think carefully."
        }
    ]
    
    # Second API call maintaining reasoning state
    payload2 = {
        "model": "gemma-2-9b-it:free",
        "messages": messages,
        "reasoning": {"enabled": True}
    }
    
    resp2 = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload2)
    )
    
    return resp2.json()
"""

if "run_js_style_openrouter_reasoning" not in content:
    content += "\n" + js_reasoning_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน OpenRouter JS Reasoning Flow สำเร็จ ===")
