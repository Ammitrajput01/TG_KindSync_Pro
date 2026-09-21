# 🏗️ SYSTEM ARCHITECTURE & TECHNICAL BLUEPRINT
## TG KindSync Pro (Enterprise Master Edition v15.0)

---

## 1. High-Level System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                            TG KINDSYNC PRO ECOSYSTEM                              |
+-----------------------------------------------------------------------------------+
                                          |
          +-------------------------------+-------------------------------+
          |                               |                               |
          v                               v                               v
+-------------------+           +-------------------+           +-------------------+
|   CORE STREAMING  |           |      DEVI AI      |           |   WEB SENTINEL    |
|      ENGINE       |           |     SUPERVISOR    |           |     DASHBOARD     |
| (tg_kindsync_pro) |           |  (devi/ + sidecar)|           | (web_dashboard.py)|
+-------------------+           +-------------------+           +-------------------+
          |                               |                               |
          v                               v                               v
+-------------------+           +-------------------+           +-------------------+
| • 512KB In-RAM    |           | • Multi-Model Hub |           | • Cyber-Glass UI  |
|   Multipart Stream|           |   (Groq/Mistral/  |           | • Emil Kowalski   |
| • Adaptive Cruise |           |    Gemini/Router) |           |   Spring Motion   |
|   Control (4-40)  |           | • Vitality Daemon |           | • Speedometer     |
| • Album Grouping  |           | • OSINT & SangMata|           |   Velocity Gauge  |
| • 16:9 Thumbnail  |           | • Saved Messages  |           | • Multi-Session   |
| • Topic Routing   |           |   AI Remote Bridge|           |   RBAC Auth       |
+-------------------+           +-------------------+           +-------------------+
          |                               |                               |
          +-------------------------------+-------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        STORAGE & DATA PERSISTENCE LAYER                           |
|  • history_core.sqlite (aiosqlite WAL + Async Commit Queue + Composite Idempotency)|
|  • devi/data/devi_memory.sqlite (Learned Skills, Embeddings & Evaluator History)  |
|  • data/dashboard_users.json (Hashed Passwords & RBAC Session Tokens)             |
|  • logs/ (Rotating Engine Telemetry, Forensic Event Streams & Error Logs)         |
+-----------------------------------------------------------------------------------+
```

---

## 2. Subsystem Deep-Dive

### 2.1 Pure Deterministic Streaming Engine (`tg_kindsync_pro.py`)
* **Streaming Protocol:** Telethon MTProto chunking with Cryptg acceleration. Uses `SaveBigFilePartRequest` (for files >= 10MB) and `SaveFilePartRequest` (for files < 10MB) directly over 512KB in-memory buffers (`bytearray`).
* **Concurrency Model:** Gigabit-ready TCP semaphore bounded to 48 sockets. Dynamic concurrency throttles automatically between 4 and 40 based on network latency and Telegram RPC responses.
* **File Reference Recovery:** Catches `FileReferenceExpiredError`, cancels in-flight chunk tasks, retrieves fresh message entities from Telegram, and resumes seamlessly up to 3 attempts.
* **Album Buffer:** Maintains a sliding deque buffer keyed by `grouped_id`. When the buffer flushes or timeout occurs (0.8s), all media items are sent concurrently as a grouped Telegram message.

### 2.2 Storage & Route-Aware Idempotency (`StateManager`)
* **Database Driver:** `aiosqlite` with SQLite WAL mode (`PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA busy_timeout=60000;`).
* **Composite Primary Key:** `(source_chat, msg_id, target_chat, target_topic)` guarantees zero duplicate deliveries even when cross-forwarding between multiple channels and topics.
* **Asynchronous Writer Queue:** DB writes pass through an in-memory queue (`asyncio.Queue(2000)`) with batch flushing to prevent database locking during high-speed parallel uploads.

### 2.3 Autonomous AI Supervisor (`devi/`)
* **Brain & Router (`devi.brain.model_router`):** Autonomous provider fallbacks across Groq (Ultra-Fast), Mistral Codestral (Coding), Google Gemini (Multimodal), and OpenRouter.
* **Vitality Daemon (`devi.evolution.vitality_daemon`):** Background worker scanning API keys, checking model provider health, and ingesting new Python patterns into SQLite memory.
* **OSINT & SangMata Engine (`devi.operator.osint_resolver`):** Global entity resolution, phone/email OSINT, and name/username history tracking.
* **Telegram Bridge (`devi.operator.telegram_bridge` & `telegram_bot.py`):** Unified conversational handler for group moderation, student assistance, and master admin alerts.

### 2.4 Luxury Web Sentinel Dashboard (`web_dashboard.py`)
* **Backend:** Asynchronous HTTP server powered by `aiohttp.web` on port `8080`.
* **Security & RBAC:** Multi-user authentication using individual cryptographic salts and SHA-256 password hashing.
* **Frontend Architecture:** Single-page application (SPA) with zero external CSS/JS CDN dependencies. Built with raw CSS3 custom properties, CSS Grid, SVG Speedometer gauges, and vanilla JavaScript real-time polling / EventSource.

---

## 3. Data Flow & Communication Lifecycle

```
[Telegram Source Message]
          |
          v
[Event Listener / iter_messages]
          |
          v
[Keyword & Media Type Filter] ---> (Dropped if excluded or non-matching)
          |
          v
[Route Idempotency Check (LRU Cache + SQLite WAL)] ---> (Skipped if already processed)
          |
          v
[MemoryStreamer: 512KB Chunks to Telegram DC]
          |
          v
[RPCGuard Execution with FloodWait Backoff]
          |
          v
[Target Chat Dispatch: SendMedia / Copy / Forward]
          |
          v
[State Update Queue: INSERT into forwarded]
          |
          v
[Telemetry Broadcast: Rich Terminal Table + Web Dashboard + Admin Saved Messages]
```
