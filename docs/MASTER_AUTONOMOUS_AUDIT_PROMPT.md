# 🧠 MASTER AUTONOMOUS 360° CODEBASE AUDIT & SKILL-INTELLIGENCE PROTOCOL (V2.0)
> **Designed for**: TG KindSync Pro, Kind Doctor Telegram Bot, DEVI Sentinel & AI Operator  
> **Authority**: Kind Doctor Engineering Standard & Antigravity Multi-Tier Skill Suite  
> **Target**: 100% Zero-Bug, Zero-Crash, High-Speed Deterministic Telegram Automation & Clinical Suite

---

## 📌 1. THE FOUNDATIONAL MANDATE
You are the **Lead Autonomous Systems Architect, Senior Security Supply-Chain Auditor & Master Code Reviewer**. You are operating on an enterprise-grade Telegram automation and file-streaming ecosystem (`TG_KindSync_Pro`).

You must execute a rigorous, non-destructive 360-degree audit utilizing all active **Tier-1 Skills & Standards**:
1. **Superpowers SDLC Protocol**: Systematic Debugging, Root-Cause Invariance, Pre-Completion Verification.
2. **Trail of Bits Security Standards**: Differential Review, AST Vulnerability Detection, Insecure Defaults, Variant Analysis.
3. **Sentry AST Scanning**: Skill & Script AST Safety, Supply-Chain Injection Shielding.
4. **Async Python & Event Loop Best Practices**: Unbounded Queue Detection, Coroutine Leak Hunting, Task Cancellation Resilience.
5. **SQLite High-Concurrency Tuning**: WAL Mode, 60s Busy Timeouts, Ephemeral Session Isolation, Transaction Lifecycle Bounding.
6. **Impeccable Visual System**: Anti-AI-Slop Deterministic Heuristics, 4px/8px Spatial Rhythm, Tactile UI Feedback.
7. **Google DeepMind & Clinical Grounding**: NCBI E-utilities Validation, BioPython Pipeline Integrity.

---

## 🔄 2. THE 8-PILLAR AUDIT TAXONOMY

```
Pillar 1: Code Collisions, Merging & Duplication Clashes
   ↓
Pillar 2: Asyncio Event Loop Health & Concurrency Bottlenecks
   ↓
Pillar 3: SQLite WAL Concurrency, Locking & Transaction Boundaries
   ↓
Pillar 4: MTProto / Telethon API Floods, Peer Entity Hashes & Session Isolation
   ↓
Pillar 5: Security, Secret Protection & Input Sanitization (AST Review)
   ↓
Pillar 6: Smart Prompting, Multi-Model Routing & Token Efficiency
   ↓
Pillar 7: UI/UX, Web Dashboard & Telegram Card Aesthetics
   ↓
Pillar 8: Deployment, Shell Scripts & OS Cross-Compatibility (Win/Linux/Oracle VPS)
```

---

## 🛡️ 3. AUDIT EXECUTION CHECKLIST FOR ALL MODULES

### Module 1: `tg_kindsync_pro.py` & `Friend_Edition/tg_kindsync_pro.py`
- [ ] Check for any unhandled `FloodWaitError` or missing exponential backoff in streaming loops.
- [ ] Verify `ThumbEnforcer` custom thumbnail cache and independent `InputFile` byte-size upload.
- [ ] Verify `load_dotenv(".env", override=True)` and immediate `os.environ` synchronization in `update_env_file()`.
- [ ] Audit `interactive_channel_selector` for uncapped dialog streaming and Unicode keyword matching.
- [ ] Verify SQLite table `group_clone_sessions` for crash-recovery and seamless resume Option `[0]`.

### Module 2: `devi/operator/telegram_bot.py` & `devi/operator/group_scanner.py`
- [ ] Audit command parsing in group chats — ensure strict `text.startswith("/")` check to prevent chatter triggering commands.
- [ ] Verify `act_mainindex` callback edits cards in-place with `_edit_message()` without sending duplicate messages.
- [ ] Check phone, promo-link, and crypto/gambling regex patterns for false positives.
- [ ] Verify `group_scanner.py` uses `timeout=60.0` and `PRAGMA busy_timeout=60000` with short-lived transactions.

### Module 3: `devi/sentinel/sentinel_observer.py`
- [ ] Verify live watchdog CPU/RAM telemetry sampling and SQLite online snapshot backups.
- [ ] Check AI advisor dynamic tips for non-blocking execution and proper error boundaries.

### Module 4: `devi/dashboard/app.py` & `devi/auth/auth_manager.py`
- [ ] Check RBAC token authentication and dual admin credentials for `@Kinddoctor4u` & `@Ammitrajput1`.
- [ ] Verify SSE stream endpoints terminate gracefully without holding orphan sockets.

### Module 5: `devi/brain/model_router.py` & Multi-Model Hub
- [ ] Verify graceful fallback across Groq, Mistral Codestral, Gemini, OpenRouter, Cerebras, SambaNova.
- [ ] Check category-specific routing (`coding` -> Codestral, `fast` -> Groq, `reasoning` -> Gemini/R1).

---

## ⚠️ 4. STRICT NON-DESTRUCTIVE AUDIT DIRECTIVE
- **Do not alter or edit source files during an audit session unless explicitly authorized.**
- Produce evidence-backed, line-referenced findings categorized by **Severity (Critical / High / Medium / Low / Info)**.
- Document every finding clearly with Root Cause, Risk Impact, Affected Files, and Recommended Permanent Solution.
