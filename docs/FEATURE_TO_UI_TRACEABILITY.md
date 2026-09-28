# FEATURE TO UI TRACEABILITY MATRIX — TG KINDSYNC PRO

**Traceability Standard**: Complete verification from underlying backend code to interactive UI controls.

---

## 1. Traceability Ledger

| Program Feature | Backend Source File | API / Interface | Dashboard UI Location | User Action | Live State Indicator | Verification Test |
|---|---|---|---|---|---|---|
| **Clean Standby State** | `web_dashboard.py` (`_build_status_dict`) | `GET /api/status` | Top 6 Bento Cards & Header | Initial page load or reset | `0.00 KB/s`, `0 Pending`, `ETA: Standby` | `tests/test_web_dashboard.py` |
| **Clean Display Reset** | `web_dashboard.py` (`handle_api_stats_reset`) | `POST /api/stats/reset` | Top Header Button & `Alt+C` | Click `[ Clean Display ]` | Instant 0 counters & Standby toast | `curl POST /api/stats/reset` |
| **Spotlight Command Palette** | `web_dashboard.py` (`COMMANDS_CATALOG`) | Keyboard Event Listener | Global Floating Modal | Press `Ctrl+K` or `Cmd+K` | Search input modal appears with actions | Keyboard navigation tests |
| **Dispatched Files Ledger** | `history_core.sqlite` (`telegram_topic_items`) | `GET /api/status` | Overview Tab Bottom Table | Filter by chip or search | Real-time table rows populated from SQLite | Direct SQLite query verification |
| **Category Filter Chips** | `web_dashboard.py` (`filterDispatchedFiles`) | Client DOM Engine | Sent Files Table Header | Click `Videos`, `Docs`, `Photos` | Filtered rows rendered with 0 latency | Tab filter click tests |
| **Live Speedometer Dial** | `web_dashboard.py` (`updateSpeedometer`) | `GET /api/status` (`current_speed_mb`) | Overview Card 5 | Automatic 1s poll | Animated SVG needle rotation & badge | Dynamic bandwidth test |
| **Engine Pause / Resume** | `web_dashboard.py` (`_toggle_pause`) | `POST /api/pause` | Header Button & `Space` | Click `Pause Engine` | Status dot turns yellow (`PAUSED`) | `curl POST /api/pause` |
| **Forwarding Route Matrix**| `history_core.sqlite` (`telegram_forward_routes`)| `GET/POST /api/routes/*` | Route Matrix Modal | Add route, toggle switch | Grid cards with active/standby state | SQLite CRUD API tests |
| **Cloud Backup Snapshot** | `devi/sentinel/telemetry_bridge.py` (`create_db_snapshot`) | `POST /api/backup` | Header Button & `Alt+S` | Click `Snapshot` | Dispatches backup file & toast | Backup verification test |
| **Dead Letter Queue (DLQ)**| `data/dlq_messages.jsonl` | `GET/POST /api/errors`, `/api/clear_dlq` | DLQ Tab Table | Search or click `Purge DLQ` | Empty table state with 100% Healthy | DLQ test suite |
| **Devi AI Copilot Chat** | `devi/brain/model_router.py` (`generate`) | `POST /api/devi/chat` | Devi AI Studio Tab | Type question or click chip | Instant streaming AI mentor response | Copilot chat tests |
| **3-Way AI Council** | `free_ai_hub/council.py` | `POST /api/devi/council` | Devi Studio & `Alt+D` | Click `AI Council Debate` | Multi-model consensus synthesis | Council CLI deliberation |
| **Multi-User RBAC & Auth** | `web_dashboard.py` (`DashboardAuthManager`) | `POST /api/auth/*` | Fullscreen Gate & Security Tab| Login, Create User, Logout | Session token & user profile widget | Auth test suite |
| **Sound FX Synthesizer** | `web_dashboard.py` (`playAudioFeedback`) | Web Audio API | Sidebar Audio Button | Click buttons, switch tabs | Multi-frequency chime feedback | Web Audio API calls |
| **Mobile Wi-Fi Pairing** | `web_dashboard.py` (`get_local_lan_ip`)| `GET /api/status` | Header Button & Modal | Click `Wi-Fi Phone URL` | Displays local IP & QR Code link | Network socket test |
