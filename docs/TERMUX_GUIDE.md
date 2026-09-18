# 📱 TGForwarder Android Tablet (Termux) Complete Setup Guide 🩺

> **Target Device:** Android Tablet / Smartphone with Termux App  
> **Python Version:** 3.10 / 3.11 / 3.12 (Termux Native)  
> **Status:** 100% Tested & Optimized (Zero Cryptg/Uvloop Compilation Errors)

---

## ⚡ Last Time Error Kyun Aaya Tha? (Why It Failed Previously)
Android Termux par standard `requirements.txt` run karne par do packages crash karte the:
1. `cryptg`: Ye C-compiler aur OpenSSL headers mangta hai jo Termux me fail ho jate hain.
2. `uvloop`: Ye Android ke bionic libc system me build nahi hota.

**Fix Done:** Humne `requirements_termux.txt` banaya hai jisme se ye dono problematic native C-extensions hata diye gaye hain. Telethon aur pura forwarder Termux me pure-python cryptography ke saath **100% smoothly aur fast** chalta hai!

---

## 🚀 4 Simple Steps to Run on Android Tablet:

### Step 1: Install Termux
- F-Droid ya GitHub se official **Termux** install karein (Google Play Store wala version purana hai).

### Step 2: Transfer & Extract Zip
1. `TGForwarder_TERMUX_ANDROID_LATEST.zip` ko apne Tablet me transfer karein (e.g. `Downloads` folder me).
2. Termux open karein aur type karein:
```bash
termux-setup-storage
cd ~/storage/downloads
cp TGForwarder_TERMUX_ANDROID_LATEST.zip ~/
cd ~
pkg install -y unzip
unzip TGForwarder_TERMUX_ANDROID_LATEST.zip -d TGForwarder
cd TGForwarder
```

### Step 3: Run 1-Click Setup
Bas ek command run karein:
```bash
bash termux_setup.sh
```
Ye script automatically:
- Saare Android dependencies install karega (Python, Clang, OpenSSL).
- Termux-safe python packages install karega bina kisi error ke.

### Step 4: Configure & Start
1. Apni `.env` check ya edit karein:
```bash
nano .env
```
*(Yahan apna `API_ID`, `API_HASH`, aur source/target chat set karein, phir `Ctrl + O`, `Enter`, `Ctrl + X`)*

2. Start Forwarder:
```bash
bash run_termux.sh
```
ya:
```bash
python main.py
```

Agar bot bhi chalana ho background me:
```bash
python -m devi.operator.telegram_bot &
```

---
**Done! Aapka Forwarder & Bot Android Tablet me bina PC ke 24/7 chalega!** 🩺✨
