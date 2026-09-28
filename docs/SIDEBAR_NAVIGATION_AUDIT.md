# Sidebar Navigation & Information Architecture Audit

## TG KindSync Pro V14.5 — Sentinel AI Mission Control

---

## 1. Information Architecture Principles
The navigation system is engineered around **real operational workflows** of Dr. Amit Singh (Kind Doctor):
1. **Monitoring & Telemetry**: High-frequency real-time observation of active channel stream velocity, SQLite WAL health, and storage ledger.
2. **Workers & Account Management**: Real multi-session Telegram worker switches, interactive OTP logins, and String Session imports.
3. **Intelligence & Error Triage**: Dead Letter Queue inspection with 1-click purge, Devi AI Copilot chat, 3-way multi-model council deliberation, and autonomous research insights.
4. **Administration & Security**: Role-based access control, PBKDF2 password change, and secure member onboarding.

---

## 2. Navigation Item Matrix

| Route ID | Label | Icon | Category | Priority | Target Workflow | Real Backend Endpoint | User Roles |
|---|---|---|---|---|---|---|---|
| `nav-overview` | **Overview** | Grid Layout | Monitoring | High | Master KPI cards, Speedometer SVG dial, Payload ledger, DB status | `GET /api/status` | Super Admin, Admin, Operator, Viewer |
| `nav-operations`| **Pipeline & Speed** | High-Voltage | Monitoring | High | 5-Category media breakdown, network transfer rate, ETA calculator | `GET /api/status` | Super Admin, Admin, Operator, Viewer |
| `nav-telegram` | **Telegram Accounts** | Satellite Dish | Management | High | Multi-session worker status, active session switcher, OTP login | `GET /api/telegram/accounts` | Super Admin, Admin |
| `nav-dlq` | **Dead Letter Queue** | Shield Alert | Management | High | Inspect failed message deliveries, search by channel/reason, purge DLQ | `GET /api/errors` | Super Admin, Admin, Operator |
| `nav-devi` | **Devi AI Studio** | Bot / AI | Intelligence | Medium | Copilot chat mentor, 3-way AI Council debate, autonomous key discovery | `POST /api/devi/chat`, `/api/devi/council` | Super Admin, Admin |
| `nav-research` | **Insights** | Lightbulb | Intelligence | Medium | Telemetry-driven optimization suggestions, multi-part chunk recommendations | `GET /api/research_insights` | Super Admin, Admin, Operator, Viewer |
| `nav-security` | **Access & Users** | Shield Key | Security & Admin | Medium | RBAC user management, PBKDF2 credential management, Change Password | `GET /api/auth/users`, `/api/auth/change_password` | Super Admin, Admin |

---

## 3. Sidebar Interaction & Motion Standards
- **Active Indicator**: Animated left accent bar with glow shadow (`box-shadow: 0 0 8px var(--accent-primary)`).
- **Hover Micro-State**: Subtle background elevation (`var(--bg-surface-elevated)`), icon scale `1.05`, and active press `scale(0.98)`.
- **Badges**: Real data binding (e.g. active worker count `#sidebar-tg-badge`, DLQ error count `#sidebar-dlq-badge`).
- **Footer**: Interactive profile widget with 1-click login switch, change password trigger, and synth audio toggle.
