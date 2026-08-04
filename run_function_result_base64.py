import time
import base64
from google import genai

try:
    client = genai.Client()

    # อ่านไฟล์ภาพและแปลงเป็น Base64 String
    image_path = "organ.png"
    with open(image_path, "rb") as img_file:
        base64_image_data = base64.b64encode(img_file.read()).decode("utf-8")

    # ตัวอย่างการส่ง Function Call Result / Tool Output กลับไปให้ Interaction
    interaction = client.interactions.create(
        agent="deep-research-preview-04-2026",
        input=[
            {"type": "text", "text": "Analyze the processed image result."},
            {
                "type": "image",
                "mime_type": "image/png",
                "data": base64_image_data,
            },
        ],
        background=True,
    )

    print(f"=== Function Result Task Started ===")
    print(f"Task ID: {interaction.id}")

    while interaction.status in ["processing", "queued", "in_progress"]:
        print("Processing Base64 image payload... (waiting 10s)")
        time.sleep(10)
        interaction = client.interactions.get(interaction.id)

    if interaction.status == "completed":
        print("\n=== Analysis Result ===")
        print(interaction.output_text)
    else:
        print(f"\n[Task Failed] Status: {interaction.status}")

except NameError as e:
    print(f"[NameError]: Missing variable -> {e}")
except Exception as e:
    print(f"[Error]: {e}")
