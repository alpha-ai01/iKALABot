import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

new_flow = """
def execute_full_flow():
    # 1. First interaction
    interaction1 = client.interactions.create(
        model="gemini-3.6-flash",
        input="I have 2 dogs in my house.",
    )
    print("Response 1:", interaction1.output_text)
    
    # 2. Second interaction using server-side state
    interaction2 = client.interactions.create(
        model="gemini-3.6-flash",
        input="How many paws are in my house?",
        previous_interaction_id=interaction1.id,
    )
    print("Response 2:", interaction2.output_text)
    return interaction2.output_text
"""

if "execute_full_flow" not in content:
    content += "\n" + new_flow

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== อัปเดตโค้ดหลักสำเร็จ ===")
