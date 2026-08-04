requirements = """pyTelegramBotAPI
google-genai
beautifulsoup4
gTTS
python-docx
requests
pydantic
ruff
pre-commit
pylint
bandit
"""

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(requirements.strip() + "\n")

print("=== อัปเดต requirements.txt รวมไลบรารีทั้งหมดเรียบร้อย ===")
