import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

image_code = """
import base64

def generate_futuristic_city_image():
    interaction = client.interactions.create(
        model="gemini-3.1-flash-image",
        input="Generate an image of a futuristic city skyline at sunset",
    )
    with open("generated_image.png", "wb") as f:
        f.write(base64.b64decode(interaction.output_image.data))
    return "generated_image.png"
"""

if "output_image.data" not in content:
    content += "\n" + image_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชันสร้างรูปภาพสำเร็จ ===")
