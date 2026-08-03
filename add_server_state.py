import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

server_state_code = """
def run_server_side_state_example():
    interaction1 = client.interactions.create(
        model="gemini-3.6-flash",
        input="I have 2 dogs in my house.",
    )
    print("Response 1:", interaction1.output_text)
    
    interaction2 = client.interactions.create(
        model="gemini-3.6-flash",
        input="How many paws are in my house?",
        previous_interaction_id=interaction1.id,
    )
    print("Response 2:", interaction2.output_text)
    return interaction2.output_text
"""

if "previous_interaction_id" not in content:
    content += "\n" + server_state_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน Server-side state สำเร็จ ===")
