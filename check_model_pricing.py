import requests

url = "https://openrouter.ai/api/v1/models"
try:
    response = requests.get(url, timeout=10)
    data = response.json()
    models = data.get("data", [])
    for m in models:
        if m["id"] == "meta-llama/llama-3.1-8b-instruct:free":
            print(f"Model: {m['id']}")
            print(f"Pricing: {m['pricing']}")
            break
    else:
        print("Model not found")
except Exception as e:
    print(f"Error: {e}")
