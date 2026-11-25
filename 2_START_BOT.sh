#!/usr/bin/env bash
# ==============================================================================
# 🤖 2. START KIND DOCTOR OPERATOR BOT (@KindDoc_bot)
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

PY_BIN="$(command -v python3 || command -v python || true)"
echo "[*] Launching Kind Doctor Operator Bot..."
"$PY_BIN" -m devi.operator.telegram_bot "$@"
