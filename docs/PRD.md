# 📋 PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Project: TG KindSync Pro (Enterprise Master Edition v15.0)
**Owner & Lead Architect:** Dr. Amit Singh (Kind Doctor)  
**Permanent Support & Master Admins:** `@Kinddoctor4u` (ID: `1553619403`) | `@Ammitrajput1` (ID: `759038032`)  
**Version Baseline:** v15.0 Enterprise  

---

## 1. Executive Summary & Vision
`TG KindSync Pro` is a high-performance, deterministic, zero-data-loss Telegram forwarding, cloning, media-streaming, and community management ecosystem. It bridges native MTProto userbots with an autonomous AI supervisor (`DEVI`), a real-time dark-mode Web Sentinel Dashboard, and Telegram bot assistant capabilities.

### Core Objectives:
1. **Zero Message Loss & Deterministic Streaming:** 512KB direct-in-RAM multipart chunking with dynamic adaptive cruise control.
2. **Route-Aware Idempotency:** SQLite WAL-mode state database preventing duplicate forwarding across any source-target-topic permutation.
3. **Deep OSINT & SangMata Intelligence:** Live username/name shift radar, global entity resolution, telecom & email intelligence, and automated member onboarding dossiers.
4. **Autonomous AI Supervisor (DEVI):** Multi-model router (Groq, Mistral Codestral, Gemini, OpenRouter) providing self-healing, continuous skill ingestion, and remote Telegram commands.
5. **Luxury Cyber-Glass Web Dashboard (Port 8080):** Emil Kowalski physics motion, live speedometer upload gauge, visual route matrix, multi-session RBAC management.
6. **100% Isolated Oracle Cloud / VPS Deployment:** 24/7 background systemd autopilot for both Main Admin and Friend Edition with zero cross-tenant interference.

---

## 2. Key User Personas
* **Persona 1: The Master Admin (Kind Doctor):** Requires full terminal TUI control, remote Saved Messages commands, multi-account switching, automated cloud backups, and zero-downtime 24/7 forwarding.
* **Persona 2: The Medical Student / Group Member:** Interacts with topic roadmaps, searchable batch indexes, subject-divider headers, and educational bot assistants without spam.
* **Persona 3: The Friend / Multi-Tenant User:** Requires 1-click isolated cloud deployment, web login via phone OTP/2FA, and zero configuration friction.

---

## 3. Core Feature Requirements Matrix

### 3.1 Streaming & Forwarding Engine (`tg_kindsync_pro.py`)
* **FR-1.1:** 24/7 Real-Time Live Message Listener with thread/topic filtering.
* **FR-1.2:** Deep History Batch Forwarder with automated pause, resume, and checkpoint watermarks.
* **FR-1.3:** Direct In-Memory 512KB multipart streaming (`SaveBigFilePartRequest`) with zero temporary disk writes.
* **FR-1.4:** Anti-FloodWait Adaptive Cruise Controller scaling worker concurrency (32 to 4) dynamically.
* **FR-1.5:** 16:9 Thumbnail Enforcer with PIL letterbox padding and automatic aspect correction.
* **FR-1.6:** Media Group / Album Preservation Buffering (up to 10 items) maintaining original sequence.
* **FR-1.7:** Smart Subject Classification (Anatomy, Pharmacology, Pathology, Surgery, etc.) with automated emoji divider headers.
* **FR-1.8:** Batch TOC Index Card Generation with clickable direct Telegram navigation links.
* **FR-1.9:** 1-Click Forum Topic Indexer & Master Group Navigation Roadmap builder.
* **FR-1.10:** Channel Cloner, Media Splitter, and Member Scraper tools.

### 3.2 Autonomous AI Supervisor & Sentinel (`devi/` & `sentinel_observer.py`)
* **FR-2.1:** Multi-Model Orchestration Router dynamically switching between Groq, Mistral, Gemini, and OpenRouter.
* **FR-2.2:** Continuous Skill Ingestion & Vitality Daemon (learning up to 50 patterns/day into SQLite memory).
* **FR-2.3:** Live Global OSINT Resolver & SangMata User Identity Shift Radar.
* **FR-2.4:** 24h Daily Performance Digests and automated SQLite snapshot backups with full timestamp naming.
* **FR-2.5:** Saved Messages Remote Center responding to `/status`, `/pause`, `/kill`, `/clean`, and natural language queries.

### 3.3 Luxury Web Sentinel Dashboard (`web_dashboard.py`)
* **FR-3.1:** High-aesthetic Cyber-Glass UI with Emil Kowalski physics-based spring animations.
* **FR-3.2:** Role-Based Access Control (RBAC) with salt+SHA256 hashed multi-user authentication.
* **FR-3.3:** Interactive Web Telegram Login (Phone Code + 2FA Cloud Password + Session Sync).
* **FR-3.4:** Real-Time Speedometer Upload Velocity Gauge & Active Chunk Streaming Progress Bar.
* **FR-3.5:** Visual Route Matrix Builder Modal for adding/editing topic routes directly in browser.
* **FR-3.6:** Dead Letter Queue (DLQ) Inspector & 1-Click Database Snapshot Backup Trigger.

### 3.4 Multi-Tenant Cloud Deployment (`deploy/`)
* **FR-4.1:** 1-Click Friend Package with automated SSH key permission fixes and background systemd service.
* **FR-4.2:** 100% isolated workspace directory (`/home/ubuntu/TG_KindSync_Friend`) with independent SQLite and session files.

---

## 4. Success Metrics & Quality Standards
1. **Message Delivery Reliability:** 99.99% successful message transfer with zero unhandled dropouts.
2. **Crash Resilience:** Graceful recovery on network drops, `FileReferenceExpiredError`, or rate limits.
3. **Aesthetic Excellence:** Zero-flicker terminal rendering and high-end visual design across Web Dashboard and Telegram cards.
4. **Security Isolation:** Zero credential leakage in logs; strict isolation between Admin and Friend instances.
