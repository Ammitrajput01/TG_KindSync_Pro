# 🚀 Telegram Kind Mode V14.0 — Complete User Manual & Setup Guide
**Enterprise Production Edition** | **Kind Doctor & Team**

---

## 🌟 Overview
**Telegram Kind Mode V14.0** is an enterprise-grade, high-performance Telegram media streaming, forwarding, and indexing suite. It streams large files (up to 2GB+) directly in-memory (RAM-to-Telegram) with zero temporary disk clutter, automatic medical subject sorting, dynamic caption formatting, interactive login verification, and mobile Telegram remote control.

---

## 🛠️ Quick 3-Step Setup for Windows PC

### Step 1: Install Dependencies
1. Make sure Python 3.10+ is installed from [python.org](https://www.python.org/downloads/) (*Ensure "Add Python to PATH" is checked during installation*).
2. Double-click **`1_INSTALL_DEPENDENCIES.bat`**.

### Step 2: Configure Telegram API (`.env`)
1. Visit [my.telegram.org](https://my.telegram.org) and login with your Telegram phone number.
2. Go to **API development tools** and copy your **API_ID** and **API_HASH**.
3. If `.env` is missing, the program will automatically prompt you to enter them when started, or you can copy `.env.example` to `.env` and fill them in manually:
   ```env
   API_ID=12345678
   API_HASH=0123456789abcdef0123456789abcdef
   SOURCE_CHAT=-100xxxxxxxxxx
   TARGET_CHAT=-100yyyyyyyyyy
   ```

### Step 3: Start Forwarding
- **Option A (Recommended)**: Double-click **`START_ALL.bat`** to launch both the **Master Engine** and **DEVI (AI Teacher & Sentinel Watchdog)** together in 1-Click!
- **Option B**: Double-click **`2_START_ENGINE.bat`** (or run `python main.py`).
- **Option C**: Double-click **`START_AI_TEACHER.bat`** for DEVI Sentinel Live HUD & Remote Control.
- **Option D**: Double-click **`START_DEVI_ALL.bat`** for the full DEVI Master System Menu (Console, Sentinel, Web Dashboard).
- If this is your first time logging in, follow the **Interactive Login Wizard**:
  - Enter your phone number with country code (e.g. `+919876543210`).
  - Check the on-screen badge to see whether Telegram sent the code to your **Telegram Mobile App**, **SMS**, or **Email**.
  - Enter the 5-digit code (and 2FA password if enabled).

---

## 🎯 Master Features Breakdown

### 1. ⚡ Ultra High-Speed In-Memory Streaming (Options 1–3)
- Zero disk-write overhead — transfers files directly from Telegram's MTProto servers through RAM to your destination channel.
- Automatically handles 2GB+ files and chunks in real-time.

### 2. 📑 Topic & Group Indexing Suite (Option 8)
- **Master Group Indexer**: Generates an interactive directory card for all forum topics in your group.
- **Single Topic Files Indexer**: Scans any specific topic (e.g. "Dr Ganga Video based MCQ") and compiles an ordered, clickable Table of Contents (`🎥 #01 • [Lecture Title](link)`) with an option to PIN the index card at the top of the topic.

### 3. 🎨 Dynamic Media Caption Studio (Option 10)
- Auto-detects media format and attaches dynamic badges:
  - `🎬 **Title**: Lecture 01.mp4` (Videos)
  - `📄 **Title**: Notes.pdf` (Documents/PDFs)
  - `🎵 **Title**: Audio Guide.mp3` (Audios)
- Custom batch tag support: `🎯 **Batch**: {Batch Name}`

### 4. 📚 Smart Subject Auto-Sorter
- Automatically orders lectures in natural curriculum sequence:
  `Anatomy 1..N` ➔ `Biochemistry 1..N` ➔ `Microbiology 1..N` ➔ `Pathology 1..N` ➔ `Surgery 1..N`

### 5. 📱 Mobile Telegram Command & AI Center (`START_AI_TEACHER.bat` / `START_ALL.bat`)
Send commands or talk directly to **DEVI** in your Telegram **Saved Messages**:
- `/status` — Live transmission speed, ETA, RAM/CPU vitals, and active file.
- `/report` — 24-Hour transfer volume summary & AI performance digest.
- `/backup` — Dispatches an instant SQLite database backup directly to your Saved Messages.
- `/errors` — Shows recent transmission failures from the Dead Letter Queue.
- `/tips` — View DEVI's real-time optimization recommendations.
- `/research <topic>` — Triggers DEVI's autonomous research agent on Telegram engineering topics.
- **Natural Language**: Ask DEVI anything (e.g. *"Devi, speed कैसी चल रही है?"* or *"Devi, is everything healthy?"*).
- `/dlq` — Dead Letter Queue status.
- `/tips` — Performance recommendations from AI Teacher.
- `/help` — Full command list.

### 6. 🌐 Live Web Dashboard & Worldwide Mobile Access
Sentinel Observer hosts an interactive dark-mode telemetry dashboard on port 8080.
- **Local Access**: Open `http://localhost:8080` on PC or `http://<LAN-IP>:8080` on Phone (same Wi-Fi).
- **Oracle Cloud Access**: When hosted on Oracle VPS, open `http://<ORACLE-PUBLIC-IP>:8080` from any phone on 4G/5G worldwide!
- **Features**:
  - Live Velocity Speedometer (Current & Peak MB/s).
  - 1-Click SQLite Cloud Backup to Telegram.
  - Remote `⏸️ Pause / ▶️ Resume` button.
  - 1-Tap DLQ failure records reset.
  - Live auto-scrolling terminal logs.

### 7. 🎥 Universal In-Topic Media Downloader & Multi-Group Forum Engine
- **In-Topic Video & Lecture Leeching:** When you drop a link in any forum topic with `/ytdl <url>` or `/upload <url>`, Kind Doctor Bot downloads the video, attaches an HD thumbnail, applies `#MedicalLecture #KindDoctor` clinical tags, and posts it **directly inside that specific Forum Topic**.
- **Multi-Group Isolation Guarantee:** If the bot is active in multiple groups (e.g. `Group Study Help 😉`, `NEET PG Hub`, `Test Medicos`), commands executed inside Group A are strictly isolated to Group A. Different groups never collide.
- **Remote Group Switching via `/setgroup`:** When interacting with the bot via **Private DM**, use `/setgroup` to view an interactive menu of all registered groups. Select your desired working group, and all subsequent DM commands (`/newtopic DAMS`, `/ytdl <link> DAMS`) automatically route to that group.
- **Dynamic Topic Creation (`/newtopic`):** Instantly create dedicated forum topics on the fly (e.g. `/newtopic DAMS`, `/newtopic Prepladder Pharmacology`).
- **Sequential Playlist Uploader:** Use `/playlist <playlist_url> [Topic]` to download entire courses or lecture modules (e.g. YouTube playlists). The bot sequentially uploads Lecture 01, Lecture 02, etc. directly into your topic in perfect curriculum order.
- **Universal Multi-Platform Support:** Works with YouTube, YouTube Shorts, Instagram Reels, Twitter/X videos, TikTok, and direct web file downloads (`.mp4`, `.pdf`, `.zip`, `.mkv`).
- **Zero Disk Waste:** Temporary media downloads and thumbnail artifacts are immediately deleted from disk once delivered to Telegram.

### 8. 🛡️ Permanent Vault Architecture (Zero Deletion Sync)
- **Immutable Backup Guarantee:** Cloned and downloaded archives are designed to serve as a **permanent backup vault**.
- **Strictly No Deletion Propagation:** If a primary source channel or group deletes messages (or is taken down), your cloned vault **NEVER deletes them**. Your study notes, video archives, and lecture collections remain permanently safe.

---

## 💡 Frequently Asked Questions (FAQ)

**Q1: Why didn't I receive an OTP on my mobile phone?**  
**A:** Telegram usually sends verification codes directly to the active official Telegram Mobile App (in the 'Telegram' chat) or to your registered login Email address, rather than via traditional SMS. Check your Telegram app and email inbox!

**Q2: What if Telegram gives a FloodWait error?**  
**A:** The engine automatically handles FloodWait, pauses gracefully with a live countdown timer, and resumes without losing any data.

**Q3: Can I pause and resume later?**  
**A:** Yes! All processed messages are durably saved in `history_core.sqlite`. If you stop and restart, it skips already forwarded messages automatically.

---

## 👑 Credits, Community & Official Support
- **Lead Developer**: Dr. Amit Singh (Kind Doctor)
- **Instagram**: [instagram.com/ammmitrajput1](https://www.instagram.com/ammmitrajput1) (`@ammmitrajput1`)
- **Telegram Support**: [@Ammitrajput1](https://t.me/Ammitrajput1)
- **Telegram Channel**: [@Kinddoctor4u](https://t.me/Kinddoctor4u)
- **WhatsApp Contact**: `Ammitrajput1`
- **Email**: `Ammitrajput1@gmail.com`
- **Public Branding**: **Kind Doctor & Team**
- **Medical Community**: **Group Study Help 😉**
