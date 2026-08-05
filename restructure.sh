#!/usr/bin/env bash
set -euo pipefail

# ปรับแต่งตามต้องการก่อนรัน
BACKUP_DIR="plugins/legacy/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# สร้างโฟลเดอร์เป้าหมาย (ตามโครงสร้างที่ต้องการ)
dirs=(handlers services ai voice image plugins models utils)
for d in "${dirs[@]}"; do
  if [ ! -d "$d" ]; then
    mkdir -p "$d"
    echo "Created dir: $d"
  fi
  # make package
  if [ ! -f "$d/__init__.py" ]; then
    printf "# package init for %s\n" "$d" > "$d/__init__.py"
    echo "Added __init__.py in $d"
  fi
done

# Mapping source -> destination (แก้ได้ตามโครงสร้างจริงของคุณ)
declare -A moves
moves["main.py"]="main.py"
moves["dispatcher.py"]="dispatcher.py"
moves["config.py"]="config.py"
moves["main_polling_bot.py"]="plugins/main_polling_bot.py"
moves["ai/gemini_api.py"]="ai/gemini_api.py"
moves["ai/openrouter_api.py"]="ai/openrouter_api.py"
moves["ai/router.py"]="ai/router.py"
moves["handlers/message_handler.py"]="handlers/message_handler.py"
moves["handlers/image_handler.py"]="handlers/image_handler.py"
moves["handlers/voice_handler.py"]="handlers/voice_handler.py"
moves["handlers/document.py"]="handlers/document.py"
moves["handlers/text.py"]="handlers/text.py"
moves["services/chat_service.py"]="services/chat_service.py"
moves["services/image_service.py"]="services/image_service.py"
moves["services/voice_service.py"]="services/voice_service.py"
moves["voice/speech_to_text.py"]="voice/speech_to_text.py"
moves["voice/text_to_speech.py"]="voice/text_to_speech.py"
moves["image/generator.py"]="image/generator.py"

# Helper: perform move (git mv if repo, else mv). If dest exists, backup source to BACKUP_DIR
is_git_repo=false
if [ -d .git ]; then is_git_repo=true; fi

for src in "${!moves[@]}"; do
  dst="${moves[$src]}"
  if [ -f "$src" ]; then
    if [ -f "$dst" ]; then
      # dest exists -> move src to backup to avoid overwrite
      mkdir -p "$(dirname "$BACKUP_DIR/$src")"
      mv -v "$src" "$BACKUP_DIR/$src"
      echo "Conflict: $dst exists. Moved $src -> $BACKUP_DIR/$src"
    else
      mkdir -p "$(dirname "$dst")"
      if $is_git_repo ; then
        git mv -v "$src" "$dst" || mv -v "$src" "$dst"
      else
        mv -v "$src" "$dst"
      fi
      echo "Moved $src -> $dst"
    fi
  else
    # source not present: warn
    echo "Not found (skipping): $src"
  fi
done

# Create stubs for new services if missing
stubs=("services/search_service.py" "services/url_service.py" "services/pdf_service.py")
for f in "${stubs[@]}"; do
  if [ ! -f "$f" ]; then
    cat > "$f" <<'PY'
"""
Stub service: PLACEHOLDER - implement actual logic.
"""
from typing import Any

class Service:
    def __init__(self, cfg: dict | None = None):
        self.cfg = cfg or {}

def init_service(*args, **kwargs) -> Any:
    raise NotImplementedError("Implement this service")
PY
    if $is_git_repo ; then git add "$f" >/dev/null 2>&1 || true; fi
    echo "Created stub: $f"
  else
    echo "Stub exists: $f"
  fi
done

# Backup any top-level extras not explicitly moved
extras=(main_polling_bot.py)
for e in "${extras[@]}"; do
  if [ -f "$e" ]; then
    mkdir -p "$BACKUP_DIR/extra"
    mv -v "$e" "$BACKUP_DIR/extra/$e" || true
    echo "Moved extra $e -> $BACKUP_DIR/extra/"
  fi
done

echo
echo "RESTRUCTURE COMPLETE. Review backup at $BACKUP_DIR"
echo "Next: run python3 fix_imports.py to update simple import paths, then run tests/lint."
