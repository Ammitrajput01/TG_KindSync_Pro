---
name: termux-android-engineering
description: Master Android Termux deployment, native C packaging, virtual environment bridging, and 24/7 background process persistence. Use when deploying Python, Telethon, or Node services on Android Termux.
---

# 📱 Termux Android Engineering & High-Performance Deployment Architecture

This skill captures the end-to-end engineering principles, failure modes, and automated recovery patterns for running production Python services on Android Termux (ARM64 / aarch64).

---

## 1. Core Architectural Constraints on Android Termux

### A. Bionic libc vs GNU glibc
- Android does NOT use GNU `glibc`; it uses Google's `Bionic libc`.
- C/C++ libraries that assume `glibc` behaviors (such as `uvloop`, `orjson`, `duckdb`, or raw `cryptg`) frequently trigger complex compilation errors or require multi-hour `CMake` source builds.
- **Rule**: Never compile heavy C extensions from source on Android Termux unless pre-compiled binaries are provided by the official Termux repository (`pkg`).

### B. The PyPI Source Compilation Trap (`CMake 4.4.4`)
- When running `pip install -r requirements.txt`, if a package (like `psutil` or `Pillow`) does not have an Android-compatible binary wheel on PyPI, pip will attempt to download the C/C++ source code and invoke `cmake` / `clang`.
- On mobile CPUs, compiling CMake can take 2+ hours and will often crash due to the Android Low Memory Killer (LMK).
- **Golden Rule**: Always enforce:
  ```bash
  python -m pip install --only-binary=:all: <packages>
  ```
  This guarantees that pip downloads pre-built wheels only and never falls into source compilation.

### C. Package Name Discrepancies
- In Termux, pip is directly bundled within the `python` package. There is **NO** package called `python-pip`. Running `pkg install python-pip` will fail.
- Heavy native libraries MUST be installed via Termux `pkg`:
  ```bash
  pkg install -y python git openssl ffmpeg python-cryptography python-psutil python-pillow
  ```

---

## 2. Virtual Environment (`.venv`) Bridging on Android

Termux's Python does not bundle standard `ensurepip` wheels. Creating a standard virtualenv often results in an empty environment or an environment unable to access Termux C libraries.

### Safe Venv Creation Pattern:
Always pass `--system-site-packages`:
```bash
if [ -d ".venv" ] && ! grep -qi "include-system-site-packages = true" .venv/pyvenv.cfg 2>/dev/null; then
    mv .venv ".venv.backup.$(date +%s)"
fi

if [ ! -f ".venv/pyvenv.cfg" ]; then
    python -m venv --system-site-packages .venv
fi
source .venv/bin/activate
```

---

## 3. Non-Interactive Dpkg & Mirror Self-Healing

When Termux updates packages, configuration conflicts (e.g. `openssl.cnf`) prompt the user with `(Y/I/N/O/D/Z) [default=N] ?`, blocking automation. Furthermore, community mirrors frequently rate-limit (HTTP 429).

### Bulletproof Non-Interactive Mirror Switch:
```bash
PREFIX_DIR="${PREFIX:-/data/data/com.termux/files/usr}"
echo "deb https://packages-cf.termux.dev/apt/termux-main stable main" > "$PREFIX_DIR/etc/apt/sources.list"
export DEBIAN_FRONTEND=noninteractive
dpkg --configure -a || true
yes '' | apt-get update -y && yes '' | apt-get install -y git -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
```

---

## 4. 24/7 Background Persistence & Screen-Off Execution

Android OS terminates background apps aggressively unless explicitly configured:
1. **CPU Wake Lock**: Must acquire `termux-wake-lock` to keep the CPU awake with the screen turned off.
2. **Battery Optimization**: User must set `Settings ➔ Apps ➔ Termux ➔ Battery ➔ Unrestricted`.
3. **Android 12+ Phantom Process Killer**: For heavy multi-process pipelines, phantom process limits can be disabled via ADB:
   ```bash
   adb shell "/system/bin/device_config put activity_manager max_phantom_processes 2147483647"
   ```

---

## 5. Universal Master Recovery Runbook

When any dependency or environment corruption occurs in Termux, execute this canonical self-healing block:

```bash
cd "$HOME/TG_KindSync_Pro" || exit 1
git pull origin main || true
dpkg --configure -a
pkg update -y
pkg install -y python git ffmpeg python-psutil python-pillow python-cryptography

if [ -d ".venv" ] && ! grep -qi "include-system-site-packages = true" .venv/pyvenv.cfg 2>/dev/null; then
    mv .venv ".venv.backup.$(date +%s)"
fi
if [ ! -f ".venv/pyvenv.cfg" ]; then
    python -m venv --system-site-packages .venv
fi
source .venv/bin/activate

python -m pip install --only-binary=:all: -r requirements-termux.txt
python -c "import telethon, aiohttp, aiosqlite, dotenv, rich, psutil, PIL, cryptography, qrcode, yt_dlp; print('ALL DEPENDENCIES VERIFIED')"
```
