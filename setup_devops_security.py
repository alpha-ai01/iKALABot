import os

# 1. สร้าง requirements.txt / package updates สำหรับเครื่องมือ Python & Node
requirements_content = """python-docx
ruff
pre-commit
pylint
bandit
"""

with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write(requirements_content.strip() + "\n")

# 2. สร้างไฟล์ตั้งค่า Pre-commit Framework (.pre-commit-config.yaml)
precommit_config = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.1
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.7
    hooks:
      - id: bandit
        args: ["-ll", "--exclude", "tests/"]
"""

with open(".pre-commit-config.yaml", "w", encoding="utf-8") as f:
    f.write(precommit_config)

# 3. สร้างไฟล์ตั้งค่า Ruff (ruff.toml)
ruff_config = """[lint]
select = ["E", "F", "I", "N", "W", "B", "UP", "PL"]
ignore = []
fixable = ["ALL"]
unfixable = []

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
"""

with open("ruff.toml", "w", encoding="utf-8") as f:
    f.write(ruff_config)

# 4. สร้างไฟล์ตั้งค่า Prettier (.prettierrc และ .prettierignore)
prettier_rc = """{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
"""

prettier_ignore = """node_modules/
dist/
build/
*.py
*.pyc
"""

with open(".prettierrc", "w", encoding="utf-8") as f:
    f.write(prettier_rc)

with open(".prettierignore", "w", encoding="utf-8") as f:
    f.write(prettier_ignore)

# 5. สร้างไฟล์ตั้งค่า SonarQube / SonarLint (sonar-project.properties)
sonar_props = """sonar.projectKey=my-python-project-key
sonar.projectName=My Python Secure Project
sonar.projectVersion=1.0

sonar.sources=.
sonar.exclusions=**/node_modules/**,**/dist/**,**/.venv/**,**/tests/**

sonar.python.version=3.10, 3.11, 3.12
sonar.python.ruff.reportPaths=ruff.json
sonar.python.bandit.reportPaths=bandit-output.json
"""

with open("sonar-project.properties", "w", encoding="utf-8") as f:
    f.write(sonar_props)

print("=== สร้างไฟล์ตั้งค่าระบบความปลอดภัยและคุณภาพโค้ดทั้งหมดเรียบร้อยแล้ว ===")
