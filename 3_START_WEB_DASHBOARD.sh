#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📊 3. START OBSIDIAN WEB COMMAND CENTER (PORT 8080)
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "[*] Launching DEVI Web Cockpit on http://127.0.0.1:8080 ..."
python web_dashboard.py "$@"

