import time
from google import genai

try:
    client = genai.Client()

    # 1. กำหนด Prompt สำหรับวิเคราะห์ภาพสัตว์และพฤติกรรม
    prompt = """Analyze the interspecies dynamics and behavioral risks present in the provided image of the African watering hole. Specifically, investigate the symbiotic relationship between the avian species and the pachyderms shown, and conduct a risk assessment for the reticulated giraffes based on their drinking posture relative to the specific predator visible in the foreground."""

    # 2. เริ่ม Multimodal Deep Research Task (ข้อความ + รูปภาพ URI) แบบ Background
    interaction = client.interactions.create(
        input=[
            {"type": "text", "text": prompt},
            {
                "type": "image",
                "mime_type": "image/jpeg",
                "uri": "https://storage.googleapis.com/generativeai-downloads/images/generated_elephants_giraffes_zebras_sunset.jpg"
            }
        ],
        agent="deep-research-preview-04-2026",
        background=True
    )

    print(f"=== เริ่มต้น Visual Analysis Task สำเร็จ ===")
    print(f"Research started: {interaction.id}")

    # 3. ลูปติดตามสถานะงานจนกว่าจะเสร็จสมบูรณ์ หรือล้มเหลว
    while True:
        interaction = client.interactions.get(interaction.id)
        if interaction.status == "completed":
            print("\n=== ผลการวิเคราะห์ภาพถ่ายและความสัมพันธ์ของสัตว์ ===")
            print(interaction.steps[-1].content[0].text)
            break
        elif interaction.status == "failed":
            print(f"\n[Task Failed] Research failed: {interaction.error}")
            break
        
        print("กำลังวิเคราะห์ภาพถ่ายและประเมินพฤติกรรม... (รอ 10 วินาที)")
        time.sleep(10)

except Exception as e:
    print(f"[Error]: {e}")
