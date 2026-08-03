import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

streaming_code = """
def stream_gemini_interaction(prompt="Explain how AI works"):
    stream = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        stream=True
    )
    results = []
    for event in stream:
        results.append(str(event))
    return results
"""

if "stream=True" not in content:
    content += "\n" + streaming_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน Streaming สำเร็จ ===")
