# DASHBOARD INTEGRATION OPPORTUNITIES — TG KINDSYNC PRO

**Document Purpose**: Identify and map high-value backend capabilities that exist in `history_core.sqlite` and `devi/` for direct dashboard integration.

---

## 1. High-Value Integration Opportunities

### 1. Forum Topics & Study Group Dossier Manager
* **Existing Backend Implementations**:
  - `telegram_group_topics` table: contains `topic_id`, `topic_title`, `group_id`, `created_at`.
  - `telegram_topic_items` table: contains 4,422 indexed medical lecture items.
* **Dashboard Integration**:
  - Interactive Forum Topic Directory tab or modal allowing search and direct message count inspection per topic (e.g. Anatomy, Physiology, Pathology, Pharmacology).

### 2. SangMata User Name Mutation & OSINT Tracker
* **Existing Backend Implementations**:
  - `member_name_changes` table: logs every student/user name mutation, former username, and timestamp.
  - `telegram_users_dossier` table: historical profile logs.
* **Dashboard Integration**:
  - Dedicated Student/User Dossier inspector in Access/Security view to search user history and verify authenticity.

### 3. Telegram Bot FAQ & Custom Command Manager
* **Existing Backend Implementations**:
  - `telegram_group_faqs` & `telegram_custom_commands` tables.
* **Dashboard Integration**:
  - 1-Click UI form to add FAQ triggers (e.g. `/links`, `/schedule`, `/notes`) and dynamic bot command responses without editing code.

### 4. Live Student Support Relay Matrix
* **Existing Backend Implementations**:
  - `telegram_relay_map` table: maps incoming student help requests to Admin Telegram IDs (`@Kinddoctor4u` & `@Ammitrajput1`).
* **Dashboard Integration**:
  - Real-time relay session status and quick reply relay terminal.
