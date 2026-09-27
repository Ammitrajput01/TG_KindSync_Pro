# 📜 TG KindSync Pro & Kind Doctor Bot — Project History & Regression Guard Log

This log permanently documents root causes, architectural patterns, historical bugs, and applied fixes across all systems.

---

## 📅 Log Entry: Sunday, 27 September 2026

### 1. Group & Topic Scanner Zero-Item Scan Issue (`/scan` & `/topicindex`)
* **Symptom**: Running `/scan` or `/topicindex` in a supergroup topic returned `Topics Registered: 0`, `Lectures/Files Indexed: 0` despite the group having 1,580+ videos and multiple forum topics.
* **Root Cause**:
  1. `devi.operator.group_scanner` looked for active Telethon user session files (`session_forwarder.session`, `session_scanner.session`, etc.).
  2. Because the main Kind Doctor Bot / forwarder was running live in the background, the SQLite session file was locked (`sqlite3.OperationalError: database is locked`).
  3. `group_scanner` fell back to `session_bot_scanner` (Telegram Bot API token).
  4. Telegram Bot API prohibits bots from calling `GetForumTopicsRequest` or fetching chat history (`iter_messages`) in forum supergroups where bots lack raw MTProto message history reader permissions. Hence, 0 topics and 0 media items were returned.
* **Permanent Fix Applied**:
  - In [devi/operator/group_scanner.py](file:///c:/TG_KindSync_Pro/devi/operator/group_scanner.py): Added isolated **ephemeral session cloning** (`temp_scan_{stem}_{pid}.session`). When the main session is locked by the live background bot, an isolated session copy is created on-the-fly, allowing the MTProto user client to connect immediately without SQLite locks or process contention, fetch all topics via `GetForumTopicsRequest`, index all 1,580+ videos/notes, and clean up the temporary session upon completion.
  - Enhanced peer resolution across all channel ID formats (with/without `-100` prefix, raw ID, and dialog iteration).

---

### 2. Interactive CLI Channel Picker Direct Listing Issue (`get_account_channels_list`)
* **Symptom**: CLI displayed `⚠️ No joined channels list returned directly by Telegram API` instead of loading the scrollable channel selector table.
* **Root Cause**:
  1. `get_account_channels_list` used `get_dialogs(limit=None)` in bulk.
  2. If the Telegram client faced concurrent access or slight network delay with the background bot, the bulk call failed and returned an empty list.
* **Permanent Fix Applied**:
  - In [tg_kindsync_pro.py](file:///c:/TG_KindSync_Pro/tg_kindsync_pro.py) and [Friend_Edition/tg_kindsync_pro.py](file:///c:/TG_KindSync_Pro/Friend_Edition/tg_kindsync_pro.py):
    1. Replaced bulk fetch with resilient streaming `iter_dialogs(limit=None)`.
    2. Added local caching (`data/channels_cache.json`) so channels load instantly even if Telegram API is momentarily congested.
    3. Added secondary fallback from `history_core.sqlite` registered groups.

---

### 4. Web Dashboard Progress Hierarchy (Total vs In-Flight File Stream)
* **Symptom**: Overview tab had duplicate floating progress panels and mode flipping (`transfer-mode-busy` vs `transfer-mode-idle`) that caused the UI cards to cycle / alternate between overall batch progress and current file stream every few seconds.
* **Root Cause**: Duplicate HTML element IDs (`active-transfer-box`, `active-file-name`, `active-file-pct`) and conflicting UI containers in [web_dashboard.py](file:///c:/TG_KindSync_Pro/web_dashboard.py).
* **Permanent Fix Applied**:
  - Removed duplicate floating top bar in [web_dashboard.py](file:///c:/TG_KindSync_Pro/web_dashboard.py).
  - Consolidated into a permanent, non-shifting 2-tier architecture:
    - **Top Tier (Card 1)**: `Comprehensive Batch Transmission & Data Payload Ledger` (Overall Total Volume, Discovered/Delivered/Queue, Master Progress Bar %, Category breakdown).
    - **Bottom Tier (Card 2)**: `In-Flight Active File Transfer & Live Stream` (Dedicated permanent container showing current active streaming file, live chunk %, byte progress, and speed; cleanly displaying standby when idle without jumping or toggling out).

---

### 5. Clean Service Auto-Stop on Exit & Auto-Resume on Reconnect
* **Feature**: Added clean session disconnection on CLI Exit (`option 16`) and added 1-click `[5] Clean Stop Services` and `[6] Resume/Restart Services` in [1_SYNC_AND_START_MY_ORACLE.bat](file:///c:/TG_KindSync_Pro/1_SYNC_AND_START_MY_ORACLE.bat).

---

### 6. Dashboard Stale / Fake Data Purge & 1-Second Live Refresh Rate
* **Symptom**: Web Dashboard was showing old/deleted session placeholder data (`4420 items`, `3182 videos`, `Johari 1st Year`) when idle or after rules were reset, and telemetry updates felt delayed.
* **Root Cause**: Backend `/api/status` had static placeholder fallbacks and frontend polled every 2.5 seconds.
* **Permanent Fix Applied**:
  - Removed all hardcoded fallback metrics. Dashboard now strictly reads live active database records, active `.env` forwarding rules, or reports clean 0s/Standby when idle.
  - Reduced frontend polling interval from 2500ms to **1000ms (1 second)** for live real-time responsiveness.

---

### 7. Permanent Word Stripping & Caption Cleaning Engine (`strip_words.txt`)
* **Status**: 100% Permanently Enabled & Active.
* **Verified**:
  - [strip_words.txt](file:///c:/TG_KindSync_Pro/strip_words.txt) is continuously loaded on every file upload, forward, cherry-pick, and group clone.
  - Removes unwanted usernames, watermarks (`Shimperd`, `@AnandxBotss`, `kirmada`, `@Yourwishhere_bot`, skull emojis, promotional URLs/links, join/credit tags) automatically before forwarding.

