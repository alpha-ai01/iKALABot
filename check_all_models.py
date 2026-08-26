import requests

url = "https://openrouter.ai/api/v1/models"
try:
    response = requests.get(url, timeout=10)
    data = response.json()
    models = data.get("data", [])
    found = False
    for m in models:
        if "llama" in m["id"].lower():
            print(f"Model: {m['id']}, Pricing: {m['pricing']}")
            found = True
    if not found:
        print("No llama models found")
except Exception as e:
    print(f"Error: {e}")
