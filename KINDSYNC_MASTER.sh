#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# TG KINDSYNC PRO - ULTIMATE TERMUX MASTER INSTALLER
# Fresh Install | Repair | Update | Dependency Check | Launch
# Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
# ============================================================

set -Eeuo pipefail

REPO="https://github.com/Ammitrajput01/TG_KindSync_Pro.git"
PROJECT="${HOME}/TG_KindSync_Pro"
PREFIX_DIR="${PREFIX:-/data/data/com.termux/files/usr}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[OK]${NC} $*"; }
info() { echo -e "${CYAN}[INFO]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

trap 'fail "Installation failed near line $LINENO. Please share the error output."' ERR

clear || true

echo ""
echo "============================================================"
echo "          TG KINDSYNC PRO - MASTER INSTALLER"
echo "============================================================"
echo ""

# ------------------------------------------------------------
# 1. TERMUX ENVIRONMENT CHECK
# ------------------------------------------------------------

[ -d "$PREFIX_DIR" ] || fail "This script must run inside Termux."

ARCH="$(uname -m)"

info "Architecture: $ARCH"
info "Home: $HOME"
info "Prefix: $PREFIX_DIR"

case "$ARCH" in
    aarch64|arm64)
        log "64-bit ARM architecture (ARM64 / aarch64) detected."
        ;;
    armv7l|armv8l|armhf|arm)
        log "32-bit ARM architecture ($ARCH) detected. Pure-Python compatibility active."
        ;;
    x86_64|amd64)
        log "64-bit x86 architecture (x86_64) detected."
        ;;
    i686|x86)
        log "32-bit x86 architecture ($ARCH) detected."
        ;;
    *)
        warn "Architecture $ARCH detected. Standard compatibility active."
        ;;
esac

# Check for obsolete Google Play Store Termux (deprecated in 2020)
if [ -f "$PREFIX_DIR/etc/apt/sources.list" ]; then
    if grep -q -E "bintray|termux\.net" "$PREFIX_DIR/etc/apt/sources.list" 2>/dev/null; then
        warn "============================================================"
        warn "⚠️ DETECTED OBSOLETE GOOGLE PLAY STORE TERMUX BUILD!"
        warn "Google Play Store stopped updating Termux in 2020."
        warn "Auto-migrating sources to official Cloudflare mirror..."
        warn "For best stability, reinstall Termux from F-Droid:"
        warn "https://f-droid.org/packages/com.termux/"
        warn "============================================================"
        echo "deb https://packages-cf.termux.dev/apt/termux-main stable main" > "$PREFIX_DIR/etc/apt/sources.list"
    fi
fi

# ------------------------------------------------------------
# 2. REPAIR INTERRUPTED PACKAGE INSTALLATION
# ------------------------------------------------------------

info "Checking package manager..."

dpkg --configure -a || true

# ------------------------------------------------------------
# 3. REPOSITORY UPDATE & MIRROR RESOLUTION
# ------------------------------------------------------------

info "Updating Termux repositories..."

# Auto-fix mirrors to official high-speed Cloudflare CDN if rate-limited
if [ -f "$PREFIX_DIR/etc/apt/sources.list" ]; then
    if grep -q -E "textcord\.xyz|mirror\.bardia\.tech|niranjan\.co|cfe\.re" "$PREFIX_DIR/etc/apt/sources.list" 2>/dev/null; then
        echo "deb https://packages-cf.termux.dev/apt/termux-main stable main" > "$PREFIX_DIR/etc/apt/sources.list"
    fi
fi

if ! pkg update -y; then
    warn "Current mirror is not responding, auto-switching to official Cloudflare mirror..."
    echo "deb https://packages-cf.termux.dev/apt/termux-main stable main" > "$PREFIX_DIR/etc/apt/sources.list"
    if ! pkg update -y; then
        warn "Cloudflare busy, falling back to Grimler..."
        echo "deb https://grimler.se/termux/termux-main stable main" > "$PREFIX_DIR/etc/apt/sources.list"
        pkg update -y || fail "Repository update failed."
    fi
fi

# ------------------------------------------------------------
# 4. INSTALL TERMUX NATIVE DEPENDENCIES
# ------------------------------------------------------------

info "Installing native Termux packages..."

# 4A. Essential native packages (Must succeed)
pkg install -y git python openssl || apt-get install -y git python openssl || fail "Could not install core packages (git/python/openssl)."

# 4B. Native C/Bionic accelerators (Installs pre-compiled; skips gracefully if unavailable on device)
info "Installing pre-compiled native packages (psutil, pillow, cryptography)..."
pkg install -y python-cryptography python-psutil python-pillow 2>/dev/null || true

# 4C. Media engine (ffmpeg) - isolated so linker errors never block the installer
info "Checking media engine (ffmpeg)..."
pkg install -y ffmpeg 2>/dev/null || true
dpkg --configure -a 2>/dev/null || true

log "Native package installation completed."

# ------------------------------------------------------------
# 5. GIT CONFIGURATION
# ------------------------------------------------------------

info "Configuring Git..."

git config --global http.version HTTP/1.1
git config --global http.postBuffer 524288000
git config --global advice.detachedHead false

# ------------------------------------------------------------
# 6. CLONE OR REPAIR PROJECT
# ------------------------------------------------------------

info "Checking project directory..."

if [ -d "$PROJECT/.git" ]; then

    log "Existing Git repository found."

    git -C "$PROJECT" remote set-url origin "$REPO"

    if [ -z "$(git -C "$PROJECT" status --porcelain)" ]; then

        info "Updating clean repository..."

        if ! git -C "$PROJECT" pull --ff-only origin main; then
            warn "Update failed. Keeping existing project files."
        fi

    else
        warn "Local modifications detected."
        warn "Skipping automatic update to protect your files."
    fi

elif [ -d "$PROJECT" ]; then

    warn "Existing non-Git project folder found."
    warn "Preserving it as a backup."

    mv "$PROJECT" "$PROJECT.backup.$(date +%s)"

    git clone --depth 1 "$REPO" "$PROJECT"

else

    info "Fresh GitHub download..."

    git clone --depth 1 "$REPO" "$PROJECT"

fi

cd "$PROJECT"

log "Project directory ready."

# ------------------------------------------------------------
# 7. VERIFY PROJECT FILES
# ------------------------------------------------------------

info "Checking essential project files..."

[ -f "tg_kindsync_pro.py" ] || \
    fail "Main application tg_kindsync_pro.py is missing."

[ -f "requirements-termux.txt" ] || \
    fail "Android requirements file is missing."

# ------------------------------------------------------------
# 8. CREATE AND REPAIR VIRTUAL ENVIRONMENT
# ------------------------------------------------------------

info "Checking Python virtual environment..."

if [ -d ".venv" ]; then

    if [ ! -f ".venv/pyvenv.cfg" ]; then

        warn "Broken virtual environment detected."

        mv .venv ".venv.backup.$(date +%s)"

    elif ! grep -qi \
        "include-system-site-packages = true" .venv/pyvenv.cfg; then

        warn "Virtual environment cannot access native Termux packages."

        mv .venv ".venv.backup.$(date +%s)"

    fi
fi

if [ ! -f ".venv/pyvenv.cfg" ]; then
    python -m venv --system-site-packages .venv
fi

source .venv/bin/activate

log "Virtual environment activated."

echo ""
python --version
python -m pip --version
echo ""

# ------------------------------------------------------------
# 9. INSTALL ANDROID-SAFE PYTHON REQUIREMENTS
# ------------------------------------------------------------

info "Installing Android-compatible Python dependencies..."

export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_NO_CACHE_DIR=1
export MAX_JOBS=1

# No pip self-upgrade.
# No source compilation.
# No CMake builds.

CORE_PACKAGES=(
    telethon
    aiohttp
    aiosqlite
    python-dotenv
    rich
)

OPTIONAL_PACKAGES=(
    "qrcode[pil]"
    yt-dlp
)

for package in "${CORE_PACKAGES[@]}"; do

    echo ""
    info "Installing $package"

    python -m pip install \
        --only-binary=:all: \
        --no-cache-dir \
        "$package" || fail "Could not install core package: $package"

done

for package in "${OPTIONAL_PACKAGES[@]}"; do

    echo ""
    info "Installing optional package: $package"

    if ! python -m pip install \
        --only-binary=:all: \
        --no-cache-dir \
        "$package"; then

        warn "Optional package skipped: $package"

    fi

done

# ------------------------------------------------------------
# 10. VERIFY CORE MODULES
# ------------------------------------------------------------

info "Running dependency verification..."

python - <<'PY'
import importlib
import sys

required = [
    "telethon",
    "aiohttp",
    "aiosqlite",
    "dotenv",
    "rich"
]

optional = [
    "psutil",
    "PIL",
    "cryptography",
    "qrcode",
    "yt_dlp"
]

failed = []

for module in required:
    try:
        importlib.import_module(module)
        print("  [OK: Core] " + module)
    except Exception as e:
        print("  [FAILED: Core] " + module + ": " + str(e))
        failed.append(module)

for module in optional:
    try:
        importlib.import_module(module)
        print("  [OK: Acceleration] " + module)
    except Exception as e:
        print("  [OPTIONAL/FALLBACK] " + module + " (Pure-Python fallback active)")

if failed:
    print("\nMissing required core modules:", failed)
    sys.exit(1)

print("\nALL REQUIRED MODULES VERIFIED.")
print("Python:", sys.version)
PY

# ------------------------------------------------------------
# 11. INITIALIZE PROJECT DIRECTORIES
# ------------------------------------------------------------

info "Preparing application directories..."

mkdir -p \
    logs \
    db_backups \
    member_backups \
    data \
    archives

# ------------------------------------------------------------
# 12. PROTECT EXISTING CONFIGURATION
# ------------------------------------------------------------

if [ ! -f ".env" ]; then

    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        log "Default .env created from .env.example."
    else
        touch ".env"
        warn "Empty .env created. Application configuration is required."
    fi

else
    log "Existing .env preserved."
fi

chmod 600 .env

# ------------------------------------------------------------
# 13. CHECK PYTHON VERSION
# ------------------------------------------------------------

PYTHON_MINOR="$(python -c 'import sys; print(sys.version_info.minor)')"
PYTHON_MAJOR="$(python -c 'import sys; print(sys.version_info.major)')"

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -gt 12 ]; then
    warn "Python 3.$PYTHON_MINOR is outside documented 3.10-3.12 range."
    warn "Core imports passed, but full application compatibility still needs testing."
fi

# ------------------------------------------------------------
# 14. INSTALLATION SUMMARY
# ------------------------------------------------------------

echo ""
echo "============================================================"
echo "              INSTALLATION SUMMARY"
echo "============================================================"

log "Termux environment ready."
log "Git repository ready."
log "Virtual environment ready."
log "Core dependencies verified."
log "Application directories initialized."
log ".env configuration preserved."

echo ""
echo "Project: $PROJECT"
echo "Python: $(python --version)"
echo ""

# ------------------------------------------------------------
# 15. WAKE LOCK
# ------------------------------------------------------------

if command -v termux-wake-lock >/dev/null 2>&1; then

    info "Activating Termux wake lock..."
    termux-wake-lock || true

else
    warn "Termux:API wake-lock command unavailable."
fi

# ------------------------------------------------------------
# 16. LAUNCH MENU
# ------------------------------------------------------------

echo ""
echo "============================================================"
echo "                 SELECT RUNNING MODE"
echo "============================================================"
echo ""
echo "1. Interactive Forwarder (Foreground / QR Login)"
echo "2. Full 24/7 Background Runner"
echo "3. Install Only - Exit"
echo "4. Open .env Configuration"
echo "5. Run Application Diagnostics"
echo ""

read -r -p "Enter option [1-5]: " choice

case "$choice" in

    1)
        echo ""
        info "Starting TG KindSync Pro..."
        exec python tg_kindsync_pro.py
        ;;

    2)
        echo ""

        if [ -f "deploy/RUN_24_7_TERMUX.sh" ]; then

            info "Starting background services..."

            bash deploy/RUN_24_7_TERMUX.sh

            echo ""
            log "Background runner command completed."
            echo "Check logs:"
            echo "tail -f logs/forwarder_service.log"
            echo "tail -f logs/bot_service.log"
            echo "tail -f logs/dashboard_service.log"

        elif [ -f "START_24_7_TERMUX.sh" ]; then
            bash START_24_7_TERMUX.sh
        else
            fail "Background runner script not found."
        fi
        ;;

    3)
        log "Installation finished. Nothing launched."
        ;;

    4)
        if command -v nano >/dev/null 2>&1; then
            nano .env
        else
            pkg install -y nano
            nano .env
        fi
        ;;

    5)
        info "Running application diagnostics..."

        python -m compileall -q tg_kindsync_pro.py devi || true

        python - <<'PY'
import importlib.util

for name in [
    "tg_kindsync_pro",
    "web_dashboard",
    "devi.operator.telegram_bot"
]:
    try:
        print(name, ":", "FOUND" if importlib.util.find_spec(name) else "NOT FOUND")
    except Exception as e:
        print(name, ":", "ERROR", e)
PY
        ;;

    *)
        warn "Invalid selection. Installation is complete."
        ;;

esac

echo ""
echo "============================================================"
echo "              TG KINDSYNC PRO MASTER"
echo "============================================================"
