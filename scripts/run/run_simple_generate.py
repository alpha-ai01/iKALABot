from google import genai

try:
    client = genai.Client()

    print("=== ส่งคำถามไปยัง gemini-3.6-flash ===")
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="How does AI work?"
    )

    print("\n=== ผลลัพธ์ ===")
    print(response.text)

except Exception as e:
    print(f"[Error]: {e}")
