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
* **Status**: 100% Permanently Enabled & Active across all engines.
* **Verified**:
  - [strip_words.txt](file:///c:/TG_KindSync_Pro/strip_words.txt) is continuously loaded on every file upload, forward, cherry-pick, and group clone.
  - Automatically strips:
    - Bot tags & Watermarks: `@Cerebellumvideosbot`, `@YourSynapse_bot`, `Dams_new_robot`, `@AnandxBotss`, `Shimperd`, `Shimperd playbold`, `@medAcadpdf`, `@yourrwishh`, `@yourwishhere_bot`, `#yourwish`, `@Whitecoatsociety_bot`, `Kirmada rockstar kirmada`, `kirmada rocket launcher`, `kirmada`, `@medbookeasy`, `@verse_medical`, `The Pirate Bay`, `DrGhost`, `yw`, `Yw`.
    - Unicode Fancy Headers: `✨ 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐄𝐃 𝐁𝐘`, `━━━━━━━✦✗✦━━━━━━━`.
    - Promotional Links: `medicalverse.in`, `https://t.me/verse_medical`, `Join [Medical Verse]...`.
    - Emojis: `☠️`, `☠`, `💀`.

---

### 8. CLI Safe Exit & Full Services Shutdown (`Option 16`)
* **Symptom / Request**: When choosing `Option 16`, user wanted the option to completely shutdown running server services (`tg-forwarder`, `tg-kinddoc-bot`, `tg-dashboard`) so that everything stops cleanly on the server, and starts back up when launching `1_SYNC_AND_START_MY_ORACLE.bat`.
* **Permanent Fix Applied**:
  - In [tg_kindsync_pro.py](file:///c:/TG_KindSync_Pro/tg_kindsync_pro.py) and [Friend_Edition/tg_kindsync_pro.py](file:///c:/TG_KindSync_Pro/Friend_Edition/tg_kindsync_pro.py):
    - Option 16 now offers a dual choice:
      - `[1] Exit CLI Menu Only` (leaves background services running).
      - `[2] Complete Server & Services Shutdown` (stops `tg-forwarder`, `tg-kinddoc-bot`, `tg-dashboard`, flushes WAL, disconnects all sessions, and terminates).

---

### 9. Main Menu Default Option `2` (Balanced Mode) & Visual Prompt Clarity
* **Symptom**: Prompt line clarity and immediate auto-selection on pressing `[Enter]`.
* **Permanent Fix Applied**:
  - Set explicit prompt string `👉 Enter Choice [1-19] (Default: 2 - Balanced Mode): `.
  - Pressing `[Enter]` on empty input immediately defaults to `2` (Balanced Mode - 12 Workers).

---

### 10. Welcome Message & Sangmata Live OSINT Biometric Resolver Protection
* **Symptom**: Welcome card and `@SangMata_beta_bot` name/username change history occasionally failed or timed out when background forwarder was active.
* **Root Cause**:
  - `devi.operator.osint_resolver` attempted to connect to `session_forwarder.session`, which was locked by the active forwarder daemon, causing `sqlite3.OperationalError: database is locked`.
  - Missing default fallback merging in `_get_group_settings()`.
* **Permanent Fix Applied**:
  - In [devi/operator/osint_resolver.py](file:///c:/TG_KindSync_Pro/devi/operator/osint_resolver.py): Added ephemeral session cloning (`temp_osint_{stem}_{pid}.session`). Now, even when the forwarder holds the main session lock, the OSINT resolver seamlessly connects with user MTProto credentials to query `@SangMata_beta_bot` and fetch full multi-year biometric name/username timelines without failure.
  - In [devi/operator/telegram_bot.py](file:///c:/TG_KindSync_Pro/devi/operator/telegram_bot.py): Hardened `_get_group_settings()` so `welcome_enabled: 1` and `join_track_enabled: 1` always remain active by default.

---

### 11. Channel Picker List Fix (`No joined channels list returned`)
* **Symptom**: Interactive channel selector in Group Cloner / Cherry Picker (`interactive_channel_selector`) showed `⚠️ No joined channels list returned directly by Telegram API` instead of displaying the scrollable list of joined groups/channels.
* **Root Cause**: The active forwarder background process held SQLite locks on `session_forwarder.session`, causing `client.iter_dialogs()` to raise `sqlite3.OperationalError: database is locked` and return an empty channel list.
* **Permanent Fix Applied**:
  - In [tg_kindsync_pro.py](file:///c:/TG_KindSync_Pro/tg_kindsync_pro.py) and [Friend_Edition/tg_kindsync_pro.py](file:///c:/TG_KindSync_Pro/Friend_Edition/tg_kindsync_pro.py): `get_account_channels_list()` now uses ephemeral session cloning (`temp_dialogs_{stem}_{pid}.session`). If the main session file is locked, it creates an instant temporary clone, fetches all 50+ joined groups & channels with MTProto user privileges, caches to `data/channels_cache.json`, and cleans up the clone.

---

### 12. 100% Clickable Direct Forum Topic Links (`/topicindex`)
* **Symptom**: Some lecture rows in `/topicindex` cards were unclickable or didn't open the direct message in Telegram Desktop/Mobile.
* **Root Cause**:
  1. Empty or whitespace-only lecture titles resulted in empty `<a href="..."></a>` tags, rendering without clickable text.
  2. Generic `https://t.me/c/<chat>/<msg_id>` links in forum supergroups were missing the `topic_id` path (`https://t.me/c/<chat>/<topic_id>/<msg_id>`), causing Telegram clients to fail resolving messages inside topics.
* **Permanent Fix Applied**:
  - In [devi/operator/telegram_bot.py](file:///c:/TG_KindSync_Pro/devi/operator/telegram_bot.py):
    - Added fallback title generator (`Lecture Material #{idx:02d}`) so no link text is ever empty.
    - Generated topic-aware direct Telegram deep links: `https://t.me/c/{clean_chat_id}/{target_t_id}/{m_id}`.
    - Wrapped titles in `<a href="..."><b>{safe_title}</b></a>` ensuring every single lecture item is rendered as a distinct, bold, 100% clickable hyperlink.

---

### 13. Auto-Scan Bot Status Notification Exclusion from Topic Index
* **Symptom**: Temporary bot notifications (e.g. `🔍 'Topic #26348' ke media files auto-scan kiye ja rahe hain...`) appeared as indexed notes (e.g. Item `#36`) in the generated `/topicindex` study cards.
* **Root Cause**: When `/topicindex` triggered an auto-scan, the temporary status notification sent by the bot was active in the topic when `group_scanner` iterated through messages. Since it was a non-command text message, it was captured as a note item.
* **Permanent Fix Applied**:
  - In [devi/operator/group_scanner.py](file:///c:/TG_KindSync_Pro/devi/operator/group_scanner.py): Added `BOT_IGNORE_MARKERS` and bot sender checks (`getattr(msg.sender, 'bot', False)` or `via_bot_id`) to completely ignore bot status banners, scan messages, and automated cards from ever being indexed.
  - Purged all legacy bot notification entries from `telegram_topic_items` in SQLite.

---

### 14. Dedicated Interactive Word & Watermark Stripping Studio (`strip_words.txt`)
* **Feature Addition**: Enhanced Word & Watermark Cleaner into a dedicated interactive manager accessible under Main Menu Option `[10] ✍️ Caption & Link Studio` -> `[1] 📝 Word & Watermark Cleaner Studio`.
* **Capabilities Added**:
  1. **📋 View Full Active Clean List**: Formatted interactive table showing all active word patterns, usernames, and sponsor watermarks in `strip_words.txt` along with replacement mappings (`Old ➔ New`).
  2. **➕ Add Word(s) with Explicit SAVE Confirmation**: Supports pasting single or batch words (separated by comma, pipe, or newlines) with a preview table and an explicit `💾 Save word(s) to strip_words.txt? (SAVE / NO)` confirmation prompt before writing.
  3. **🗑️ Delete Word / Watermark**: Instant removal of any pattern by selecting its list index `#` or typing the exact text.
  4. **🔄 Edit Word Replacements**: Direct editing of `REPLACE_WORDS` mapping with auto-save to `.env`.
  5. **📂 Open in Notepad**: 1-click launch of `strip_words.txt` in the system text editor for bulk edits.
  6. **🧹 Deduplicate & Clean**: 1-click cleanup to eliminate duplicate entries and empty lines while preserving section headers.
  7. **Live Cache Auto-Reload**: Updates invalidate `_CLEAN_RULES_CACHE` immediately so all running forwarding and caption processes apply the new clean rules without requiring a restart.

---

### 15. Group & Topic Scanner MTProto User Session Link & SQLite Lock Immunity
* **Symptom**: Running `/scan` or `/mainindex` via `@KindDoc_bot` in forum supergroups resulted in only 1 topic being registered (`Index`) and threw `The API access for bot users is restricted (caused by GetRepliesRequest)` or `sqlite3.OperationalError: database is locked`.
* **Root Cause**:
  1. Telegram Bot API strictly forbids bot tokens from invoking `messages.getForumTopics` and `GetRepliesRequest` directly in forum supergroups.
  2. The scanner subprocess fell back to bot mode when the main user session was unlinked on VPS.
  3. Long-held SQLite transactions during mass topic harvesting triggered database lock errors against the active forwarder daemon.
* **Permanent Fix Applied**:
  - In [devi/operator/group_scanner.py](file:///c:/TG_KindSync_Pro/devi/operator/group_scanner.py):
    - Restored and linked the authorized primary user MTProto session (`Kind` ID `1553619403`).
    - Implemented `get_db_conn()` with `timeout=60.0`, `PRAGMA busy_timeout=60000;`, and `PRAGMA synchronous=NORMAL;`.
    - Shortened transaction lifecycles and added exponential backoff retries for concurrent multi-process writes.
    - Successfully auto-scanned all 95 forum topics and 1,000+ lectures/PDFs into SQLite for instant `/mainindex` and `/topicindex` generation.

---

### 16. Instant 1-Click Auto-Resume Option `[0]` / `[R]` in Main Menu
* **Feature Addition**: Added Option `[0]` / `[R]` to `tg_kindsync_pro.py` and `Friend_Edition/tg_kindsync_pro.py`.
* **Behavior**:
  - Displays a persistent **⚡ ACTIVE LAST ROUTE** banner at the top of the main menu (`Source ID -> Destination ID`).
  - Pressing `0` or `R` instantly resumes the previous streaming/forwarding job from the exact last processed message ID without re-prompting for channel IDs or topic configurations.

---

### 17. Telethon Video Upload Freeze / Thumbnail Upload Bug Resolution
* **Symptom**: Streaming/cloning large videos (500MB+) with custom 16:9 thumbnails froze for hours without progressing or uploading.
* **Root Cause**: Telethon's internal `_file_to_media` passes `file_size=file_size` (the 500MB video size) when uploading the thumbnail file. Telethon expects 500MB of thumbnail bytes, causing an infinite EOF stall.
* **Permanent Fix Applied**:
  - In `ThumbEnforcer`: Implemented `async def get_input_file(client)` with in-memory caching. The thumbnail is uploaded independently as an `InputFile` with its own true byte size, and passed as `thumb=input_file` directly to `client.send_file()`. Large video uploads now proceed at maximum network velocity without stalls.

---

### 18. Watermark Cleaning Engine Unicode & Symbol Support
* **Feature Addition**: Added support for non-ASCII prefixes and unicode small-caps in `strip_words.txt` (e.g. `📇 Exᴛʀᴀᴄᴛᴇᴅ Bʏ : @medicos_saviourbot 💎`).
* **Fix**: Updated regex compilation in `apply_clean_rules()` so that `\b` word boundary is only applied to ASCII alphanumeric leading characters, preventing silent matching failures on emoji and unicode symbols.

---

### 19. Kind Doctor Admin Direct Messaging & Anonymous Group Replies
* **Feature Addition**: Added admin messaging commands to `devi/operator/telegram_bot.py`:
  1. `/say <message>` & `/dr <message>`: In group chats, when replying to a student, deletes the admin's command and posts an anonymous authoritative response from `👨‍⚕️ Kind Doctor`.
  2. `/send <@username or user_id> <message>` & `/pm <target> <message>`: Direct DM from the bot to any student with automated database username-to-ID resolution.
  3. `/sendlink <@username or user_id>`: Automatically delivers a 30-minute single-use disposable invite link directly to the student.
  4. Added `2_START_KIND_DOCTOR_BOT.bat` 1-click launcher in root and `tools/launchers/`.
