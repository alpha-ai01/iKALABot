import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

# เพิ่มฟังก์ชันสำหรับการเรียกใช้งาน client.interactions.create และดึงผลลัพธ์พร้อม Citation ตามรูปแบบใหม่
interaction_code = """
def call_gemini_interaction(prompt_text, media_files=None, use_search=True):
    tools_config = [{"type": "google_search"}] if use_search else []
    
    # เรียกใช้งานผ่าน client.interactions.create ตามโครงสร้างใหม่
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt_text,
        tools=tools_config
    )
    
    response_text = ""
    citations = []
    
    # ดึงข้อความและ Annotation (Citations) จาก step
    if hasattr(interaction, 'steps') and interaction.steps:
        for step in interaction.steps:
            if step.type == "model_output":
                for content_block in step.content:
                    if content_block.type == "text":
                        response_text += content_block.text
                        if content_block.annotations:
                            for annotation in content_block.annotations:
                                if annotation.type == "url_citation":
                                    citations.append(f"[{annotation.title}]({annotation.url})")
                                    
    # หากผลลัพธ์เป็นโครงสร้าง dict หรือ JSON คล้ายโครงสร้าง API Response ดิบ
    elif isinstance(interaction, dict):
        steps = interaction.get("steps", [])
        for step in steps:
            if step.get("type") == "model_output":
                for content_block in step.get("content", []):
                    if content_block.get("type") == "text":
                        response_text += content_block.get("text", "")
                        for annotation in content_block.get("annotations", []):
                            if annotation.get("type") == "url_citation":
                                citations.append(f"[{annotation.get('title')}]({annotation.get('url')})")

    if citations:
        response_text += "\\n\\n**Citations:**\\n" + "\\n".join(citations)
        
    return response_text
"""

if "def call_gemini_interaction" not in content:
    content += "\n" + interaction_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน Interactions สำเร็จ ===")
