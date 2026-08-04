import time
from google import genai

try:
    client = genai.Client()

    # 1. เริ่มงานเช็กสถานะ Deployment ผ่าน MCP Server Tool
    interaction = client.interactions.create(
        agent="deep-research-preview-04-2026",
        input="Check the status of my last server deployment.",
        tools=[
            {
                "type": "mcp_server",
                "name": "Deployment Tracker",
                "url": "https://mcp.example.com/mcp",
                "headers": {"Authorization": "Bearer my-token"},
            }
        ],
        background=True,
    )

    print(f"=== เริ่มต้น Deployment Status Task สำเร็จ ===")
    print(f"Task ID: {interaction.id}")
    print(f"Status: {interaction.status}")

    # 2. ติดตามสถานะจนกว่าการเชื่อมต่อ MCP Server และดึงข้อมูลจะเสร็จสิ้น
    while interaction.status in ["processing", "queued", "in_progress"]:
        print("กำลังดึงข้อมูลสถานะจาก MCP Server... (รอ 5 วินาที)")
        time.sleep(5)
        interaction = client.interactions.get(interaction.id)

    # 3. แสดงผลลัพธ์การตรวจสอบเมื่อเสร็จสมบูรณ์
    if interaction.status == "completed":
        print("\n=== ผลการตรวจสอบสถานะ Deployment ===")
        print(interaction.output_text)
    else:
        print(f"\n[Task Failed] สถานะ: {interaction.status}")

except Exception as e:
    print(f"[Error]: {e}")
