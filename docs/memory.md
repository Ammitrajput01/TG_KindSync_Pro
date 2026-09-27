# 🧠 SYSTEM MEMORY & PERSISTENT KNOWLEDGE BASE
## TG KindSync Pro (Enterprise Master Edition v15.0)

---

## 1. Project Identity & Key Context
* **Project Name:** `TG KindSync Pro`
* **Lead Creator & Owner:** Dr. Amit Singh (Kind Doctor)
* **Master Admin 1:** `@Kinddoctor4u` (ID: `1553619403`)
* **Master Admin 2:** `@Ammitrajput1` (ID: `759038032`)
* **Core Function:** High-speed, deterministic Telegram MTProto userbot forwarding, album grouping, forum topic routing, batch indexing, and autonomous AI community management.
* **Branding Guideline:** Strictly **TG KindSync Pro (Kind Doctor & Team)**. Never use or mention AyuGram/Eugram.

---

## 2. Established Codebase Patterns & Invariants
1. **Streaming Architecture:**
   * Uses 512KB multipart chunks in RAM (`SaveBigFilePartRequest` / `SaveFilePartRequest`).
   * Dynamic concurrency governed by `CruiseController` (scales between 4 and 40).
   * Gigabit TCP semaphore bound to 48 sockets.
2. **Database & Idempotency:**
   * SQLite WAL mode with `aiosqlite` and asynchronous queue commits.
   * Composite unique key: `(source_chat, msg_id, target_chat, target_topic)` prevents duplicate delivery across all routes.
3. **OSINT & SangMata Intelligence:**
   * Telegram MTProto API provides only *current* profile details.
   * Historical name/username records (2019–2026) are collected via continuous group logging and live userbot relay to OSINT databases.
4. **Autonomous AI Supervisor (DEVI):**
   * Multi-Model Router with free provider fallback: Groq (fast), Mistral Codestral (coding), Gemini (multimodal), OpenRouter (aggregator).
   * Vitality Daemon performs autonomous key discovery and continuous pattern learning into SQLite memory.
5. **Deployment & Backup Standards:**
   * All backup/export filenames must follow: `[prefix]_[Day]_[Date]-[Month]-[Year]_[Time-12hAM-PM].[ext]`.
   * Standard caption format: `[Day], [Date] [Month] [Year] | [HH]:[MM] [AM/PM]`.
   * NEVER push to GitHub or deploy to Oracle Cloud VPS without explicit user instruction.

---

## 3. Known Gotchas & Resolved Edge Cases
* **FileReferenceExpiredError:** Automatically handled by `MemoryStreamer` — refreshes message entity from Telegram and retries up to 3 times.
* **Shadowed Indexer Cleanup:** Obsolete first definition of `run_master_group_indexer` (261 lines) was removed in v15.0; active version at line 6813 remains intact.
* **Friend Edition Systemd Headless Mode:** Headless cloud instances must not prompt for interactive terminal input without pre-configured `.env` parameters.
