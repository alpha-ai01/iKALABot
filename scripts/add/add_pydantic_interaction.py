import re

filename = "main.py"

with open(filename, "r", encoding="utf-8") as f:
    content = f.read()

# เพิ่มคลาส Pydantic และฟังก์ชัน Structured Output เข้าไปใน main.py หากยังไม่มี
pydantic_code = """
from pydantic import BaseModel, Field
from typing import List, Optional

class Recipe(BaseModel):
    recipe_name: str = Field(description="Name of the recipe.")
    ingredients: List[str] = Field(description="List of ingredients.")
    prep_time_minutes: Optional[int] = Field(description="Prep time in minutes.")

def get_structured_recipe(prompt="Give me a recipe for banana bread"):
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Recipe.model_json_schema()
        },
    )
    recipe = Recipe.model_validate_json(interaction.output_text)
    return recipe
"""

if "class Recipe" not in content:
    content += "\n" + pydantic_code

with open(filename, "w", encoding="utf-8") as f:
    f.write(content)

print("=== เพิ่มฟังก์ชัน Structured Output ด้วย Pydantic สำเร็จ ===")
