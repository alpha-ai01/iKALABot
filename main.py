import os
import requests
from google import genai
from google.genai import types

# Initialize Gemini Client
client = genai.Client()

def call_gemini_with_tools(prompt_text, tools_config=None):
    config = types.GenerateContentConfig(tools=tools_config) if tools_config else None
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt_text,
        config=config
    )
    return response

def call_openrouter_api(messages, tools=None):
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "anthropic/claude-3.5-sonnet",
        "input": messages,
        "max_output_tokens": 9000
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
        
    response = requests.post("https://openrouter.ai/api/v1/responses", headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    print("Telegram Chatbot configuration updated successfully with Gemini 3.6 Flash and Claude 3.5 Sonnet.")

# เพิ่ม Health Check Endpoint รองรับ GET และ HEAD สำหรับ UptimeRobot
try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route("/", methods=["GET", "HEAD"])
    @app.route("/health", methods=["GET", "HEAD"])
    def health_check():
        return "OK", 200
        
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=10000)
except ImportError:
    pass
