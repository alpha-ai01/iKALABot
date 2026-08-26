import requests

url = "https://openrouter.ai/api/v1/models"
try:
    response = requests.get(url, timeout=10)
    data = response.json()
    models = data.get("data", [])
    for m in models:
        if m.get("pricing", {}).get("prompt") == "0":
            print(f"Free Model: {m['id']}")
except Exception as e:
    print(f"Error: {e}")
