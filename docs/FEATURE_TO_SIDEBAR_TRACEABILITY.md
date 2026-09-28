# Feature to Sidebar Traceability Matrix

## TG KindSync Pro V14.5 — Sentinel AI Mission Control

This matrix maps every underlying program feature directly to its primary entry point in the navigation sidebar, associated user actions, and underlying Python backend implementation.

---

## 1. Traceability Mapping

| Program Subsystem | Backend Module / Function | Sidebar Entry | Primary User Action | Real-Time State Source | Verification Status |
|---|---|---|---|---|---|
| **Real-Time Telemetry** | `web_dashboard.py` (`_build_status_dict`) | **Overview** (`#nav-overview`) | Inspect 6 KPI cards, SVG speedometer, active topic | `history_core.sqlite` + Telemetry | Verified Live (200 OK) |
| **Pipeline Rate Engine** | `web_dashboard.py` (`formatDynamicSpeed`) | **Pipeline & Speed** (`#nav-operations`) | View 5-category breakdown (Videos, Docs, Photos, Audio, Text) | `engine_telemetry.json` | Verified Live (200 OK) |
| **Multi-Worker Hub** | `TelegramWebLoginManager` (`get_accounts_summary`) | **Telegram Accounts** (`#nav-telegram`) | Switch active session, Connect phone via OTP, Import String Session | `*.session` SQLite files | Verified Live (200 OK) |
| **DLQ Error Recovery** | `web_dashboard.py` (`_get_dlq_errors_list`, `clear_dlq`) | **Dead Letter Queue** (`#nav-dlq`) | Search error reasons, purge dead letter queue | `dead_letter.jsonl` | Verified Live (200 OK) |
| **Devi AI Copilot** | `ModelRouter.generate`, `AICouncil.deliberate` | **Devi AI Studio** (`#nav-devi`) | Chat with Devi AI Mentor, convene 3-way AI Council debate, key hunt | Universal Free AI Hub | Verified Live (200 OK) |
| **Autonomous Insights** | `improvement_queue.json`, `_toggle_insight_read` | **Insights** (`#nav-research`) | Review telemetry optimizations, mark suggestions as read/dismissed | `improvement_queue.json` | Verified Live (200 OK) |
| **RBAC & Security** | `DashboardAuthManager` (`change_password`, `create_user`) | **Access & Users** (`#nav-security`) | Update password, onboard new operators/viewers, delete user | `dashboard_users.json` (PBKDF2) | Verified Live (200 OK) |
| **Database Snapshot** | `telemetry_bridge.create_db_snapshot` | **Topbar & HUD** (`Alt+S`) | Trigger immediate WAL database backup snapshot | `history_core.sqlite` | Verified Live (200 OK) |
| **Command Palette** | `COMMANDS_CATALOG` (`openCommandPalette`) | **Global HUD** (`Ctrl+K`) | Fast keyboard navigation across all 18 actions | In-memory command engine | Verified Live (200 OK) |
| **Audio Synthesizer** | Web Audio API Oscillator | **Sidebar Footer** (`#audio-toggle-btn`) | Toggle micro-interaction synthesizer audio feedback | Web Audio Context | Verified Live (200 OK) |
