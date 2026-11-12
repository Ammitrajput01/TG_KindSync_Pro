#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 🤖 2. START KIND DOCTOR TELEGRAM OPERATOR BOT (@KindDoc_bot)
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python -m devi.operator.telegram_bot "$@"

