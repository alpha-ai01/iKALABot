import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

openrouter_reasoning_code = """
import requests
import json

def run_openrouter_reasoning_flow(api_key="<OPENROUTER_API_KEY>"):
    # First API call with reasoning enabled
    response = requests.post(
      url="https://openrouter.ai/api/v1/chat/completions",
      headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
      },
      data=json.dumps({
        "model": "gemma-2-9b-it:free",
        "messages": [
            {
              "role": "user",
              "content": "How many r's are in the word 'strawberry'?"
            }
          ],
        "reasoning": {"enabled": True}
      })
    )

    res_json = response.json()
    if 'choices' not in res_json:
        return res_json
        
    msg = res_json['choices'][0]['message']

    # Preserve assistant message along with reasoning_details for multi-turn reasoning
    messages = [
      {"role": "user", "content": "How many r's are in the word 'strawberry'?"},
      {
        "role": "assistant",
        "content": msg.get('content'),
        "reasoning_details": msg.get('reasoning_details')
      },
      {"role": "user", "content": "Are you sure? Think carefully."}
    ]

    # Second API call maintaining reasoning state
    response2 = requests.post(
      url="https://openrouter.ai/api/v1/chat/completions",
      headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
      },
      data=json.dumps({
        "model": "gemma-2-9b-it:free",
        "messages": messages,
        "reasoning": {"enabled": True}
      })
    )
    
    return response2.json()
"""

if "run_openrouter_reasoning_flow" not in content:
    content += "\n" + openrouter_reasoning_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน OpenRouter Reasoning สำเร็จ ===")
