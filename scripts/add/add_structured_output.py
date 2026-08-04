import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

# เพิ่มโค้ดตัวอย่าง structured output ลงไปในไฟล์หลักหากยังไม่มี
structured_code = """
from pydantic import BaseModel, Field
from typing import List, Optional

class Recipe(BaseModel):
    recipe_name: str = Field(description="Name of the recipe.")
    ingredients: List[str] = Field(description="List of ingredients.")
    prep_time_minutes: Optional[int] = Field(description="Prep time in minutes.")

def generate_structured_recipe(prompt_text="Give me a recipe for banana bread"):
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt_text,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Recipe.model_json_schema()
        }
    )
    recipe = Recipe.model_validate_json(interaction.output_text)
    return recipe
"""

if "class Recipe" not in content:
    content += "\n" + structured_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่ม Structured Output สำเร็จ ===")
