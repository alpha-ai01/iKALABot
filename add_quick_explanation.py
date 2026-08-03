import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

quick_code = """
def explain_ai_briefly():
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input="Explain how AI works in a few words"
    )
    print("AI Explanation:", interaction.output_text)
    return interaction.output_text
"""

if "explain_ai_briefly" not in content:
    content += "\n" + quick_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชันอธิบาย AI แบบสั้นสำเร็จ ===")
