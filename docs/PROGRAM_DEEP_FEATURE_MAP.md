# PROGRAM DEEP FEATURE MAP — TG KINDSYNC PRO

**System Name**: TG KindSync Pro & Sentinel AI Command Center  
**Repository Version**: v14.5 Enterprise Masterpiece  
**Architect**: Dr. Amit Singh (Kind Doctor)  
**Analysis Date**: Monday, 28 September 2026  
**Security & Architecture Classification**: Production Operational Command Center  

---

## 1. Executive Program Architecture

```
                                 ┌──────────────────────────────────────────────────────────┐
                                 │                TG KINDSYNC PRO ECOSYSTEM                 │
                                 └────────────────────────────┬─────────────────────────────┘
                                                              │
                    ┌─────────────────────────────────────────┼────────────────────────────────────────┐
                    │                                         │                                        │
     ┌──────────────┴──────────────┐           ┌──────────────┴──────────────┐          ┌──────────────┴──────────────┐
     │  CORE TELEGRAM MTPROTO      │           │     DEVI SENTINEL BRAIN     │          │  DECOUPLED WEB COMMAND CTR   │
     │  tg_kindsync_pro.py         │           │     devi/ & free_ai_hub/    │          │  web_dashboard.py            │
     └──────────────┬──────────────┘           └──────────────┬──────────────┘          └──────────────┬──────────────┘
                    │                                         │                                        │
                    ▼                                         ▼                                        ▼
   ┌─────────────────────────────────┐       ┌─────────────────────────────────┐      ┌─────────────────────────────────┐
   │ • 8x Fast Parallel Chunk Stream │       │ • Multi-Model AI Router         │      │ • Modern Cyber-Glass SPA UI     │
   │ • Idempotent WAL SQLite Ledger  │       │ • Autonomous Key Discovery      │      │ • PBKDF2 Salted Multi-User Auth │
   │ • Dynamic Forwarding Router     │       │ • 3-Way AI Council Consensus    │      │ • Real-time Telemetry Bridge    │
   │ • FloodWait Auto-Pacing (0 loss)│       │ • Vitality Autonomous Daemon    │      │ • Spotlight Command Palette ⌘K  │
   │ • Auto-Topic Categorization     │       │ • OSINT / Dossier Mutation Log  │      │ • Forward Route Matrix CRUD     │
   └────────────────┬────────────────┘       └────────────────┬────────────────┘      └────────────────┬────────────────┘
                    │                                         │                                        │
                    └─────────────────────────────────────────┼────────────────────────────────────────┘
                                                              │
                                                              ▼
                                             ┌─────────────────────────────────┐
                                             │       PERSISTENT STATE & DB     │
                                             │ • history_core.sqlite (24 tbls) │
                                             │ • engine_telemetry.json         │
                                             │ • engine_control.json           │
                                             │ • dlq_messages.jsonl            │
                                             │ • dashboard_auth.json (PBKDF2)  │
                                             └─────────────────────────────────┘
```

---

## 2. Deep Module-by-Module Technical Map

### Module 1: `tg_kindsync_pro.py` (Core MTProto Streaming Engine)
* **Purpose**: Primary high-throughput deterministic Telegram message, video, document, and album cloner/forwarder. Handles direct MTProto TCP connections via Telethon.
* **Inputs**:
  - Environment variables: `API_ID`, `API_HASH`, `SOURCE_CHAT`, `TARGET_CHAT`, `SOURCE_TOPIC`, `TARGET_TOPIC`, `FORWARDING_RULES`.
  - Telegram events: `events.NewMessage`, `events.MessageEdited`, channel history scans.
* **Outputs**:
  - Dispatched messages to Telegram destination groups/topics.
  - Telemetry state dumps to `data/engine_telemetry.json`.
  - Transaction logs to SQLite database (`history_core.sqlite`).
* **Dependencies**: `telethon`, `aiosqlite`, `sqlite3`, `cryptg` (optional C-acceleration), `Pillow`.
* **State Owned**:
  - Active batch transfer progress, connection state, speed (KB/s, MB/s, Mbps), active file chunk counter, floodwait backoff timer.
* **Persistence**:
  - `history_core.sqlite` (tables: `forwarded`, `source_watermarks`, `topic_watermarks`, `telegram_topic_items`).
* **User-Facing Relevance**: High. Dashboard must monitor real speed, batch ETA, active file transfer, and allow pause/resume.
* **Operational Controls**:
  - `Pause / Resume Engine` (via `engine_control.json`).
  - `Bandwidth Throttling` (slider rate limit).
  - `Clean Display Counters` (reset session stats).
* **Monitoring Signals**: Current speed, peak speed, completed files, remaining files, storage GB, active file progress (%), floodwaits throttled.
* **Failure Modes**: Telegram FloodWaitError (420), FileReferenceExpiredError, ChatForwardsRestrictedError, RPC connection drops.
* **Recovery Methods**: Automatic exponential backoff pacing, dynamic token refresh, DLQ logging to `dlq_messages.jsonl`.

---

### Module 2: `web_dashboard.py` (Enterprise Mission Control Server)
* **Purpose**: Standalone, decoupled aiohttp Web server providing the production SPA dashboard, REST APIs, user authentication, and system controls.
* **Inputs**:
  - Browser HTTP requests (REST API endpoints: `/api/status`, `/api/auth/login`, `/api/auth/change_password`, `/api/routes`, `/api/backup`, `/api/pause`, `/api/stats/reset`, `/api/devi/chat`, `/api/devi/council`).
  - Persistent state files: `history_core.sqlite`, `data/engine_telemetry.json`, `engine_control.json`, `dlq_messages.jsonl`, `data/dashboard_auth.json`.
* **Outputs**:
  - HTML5/CSS3/JavaScript SPA payload (Obsidian Cyber-Glass theme, Emil Kowalski physics motion, Outfit + Plus Jakarta Sans + JetBrains Mono fonts).
  - Real-time JSON telemetry payloads.
* **Dependencies**: `aiohttp` (or fallback raw async TCP server), `sqlite3`, `hashlib`, `secrets`.
* **State Owned**:
  - Active auth session tokens, in-memory rate-limiter, WebSocket/polling clients.
* **Persistence**:
  - `data/dashboard_auth.json` (PBKDF2 salted password hashes, user roles, session tokens).
* **User-Facing Relevance**: Core visual and operational interface for the user and team members.
* **Operational Controls**:
  - Full CRUD on Forwarding Routes, Cloud Snapshot trigger, DLQ purge, User Management, Password Change, Sound FX toggle, Command Palette (`Ctrl+K`).
* **Monitoring Signals**: Uptime, CPU/RAM vitals, Lan/Wi-Fi pairing URL, active worker identity, live sent files ledger.
* **Failure Modes**: Port conflict (8080), corrupted JSON state, unhandled exception in telemetry read.
* **Recovery Methods**: Non-blocking try-except guards with fallback values, atomic file writing with `.tmp` swap.

---

### Module 3: `devi/brain/model_router.py` & `free_ai_hub/` (Universal AI Engine)
* **Purpose**: Autonomous multi-model orchestrator routing prompts to Groq (Llama 3.3 70B), Mistral (Codestral), Google Gemini (2.0 Flash), and OpenRouter (DeepSeek R1).
* **Inputs**: Natural language prompts, system architectural health logs, user questions.
* **Outputs**: Structured responses, architectural audit opinions, automated code fixes.
* **Dependencies**: `aiohttp`, `httpx`, `free_ai_hub.cli`.
* **State Owned**: Model provider latency metrics, active key pools, fallback tiers.
* **Persistence**: `research_reports/improvement_queue.json`, `research_reports/dismissed_insights.json`.
* **User-Facing Relevance**: Devi AI Studio tab, Quick Prompt chips, 3-Way Council Deliberation.
* **Operational Controls**: `Run Autonomous Key Hunt`, `Convene AI Council Debate`, `Voice Briefing (Web Speech API)`.
* **Monitoring Signals**: Provider latency (ms), token generation speed, model consensus synthesis.
* **Failure Modes**: Upstream rate-limit (429), API key invalidation, timeout.
* **Recovery Methods**: Dynamic multi-provider automatic failover cascade (Groq -> Mistral -> Gemini -> OpenRouter).

---

### Module 4: `devi/sentinel/telemetry_bridge.py` & Database Layer (`history_core.sqlite`)
* **Purpose**: High-performance SQLite persistence layer operating in WAL mode. Manages idempotency, forum group topic indexing, user dossiers, and forwarding routes.
* **Inputs**: Topic creation events, file dispatch records, forward route configurations.
* **Outputs**: Normalized SQL queries, offline database snapshots (`export_backups/`).
* **Dependencies**: `sqlite3`, `aiosqlite`.
* **State Owned**:
  - 24 Database Tables (including `forwarded`, `telegram_topic_items`, `telegram_group_topics`, `telegram_forward_routes`, `telegram_users_dossier`, `member_name_changes`).
* **Persistence**: `history_core.sqlite`, `history_core.sqlite-wal`.
* **User-Facing Relevance**: Powers the Route Matrix, Sent Files Ledger, and Backup Engine.
* **Operational Controls**: `Online Snapshot Generation`, `Add/Toggle/Delete Forwarding Route`.
* **Monitoring Signals**: Dispatched files count, total discovered database items, route synchronization status.
* **Failure Modes**: SQLite database locked (`busy_timeout`), disk full.
* **Recovery Methods**: WAL journal mode, 10.0s connection timeout, retry loops with thread delegation.

---

### Module 5: `devi/evolution/vitality_daemon.py` (Self-Healing Watchdog)
* **Purpose**: Background vitality daemon continuously monitoring process health, Telegram session freshness, and research improvement queues.
* **Inputs**: System process status, memory footprint, session heartbeat.
* **Outputs**: Health summaries, alert notifications to `@Kinddoctor4u` & `@Ammitrajput1`.
* **Dependencies**: `asyncio`, `psutil`.
* **State Owned**: Continuous vitality score (0-100), uptime counter.
* **Persistence**: `logs/sentinel_observer.log`.
* **User-Facing Relevance**: Powers the System Vitals panel and status dots in the dashboard.
* **Operational Controls**: Key hunt trigger, self-healing reboot.
* **Monitoring Signals**: Vitality health percentage, auto-pacer status.
