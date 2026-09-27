# 🛡️ SUPREME RULES, SECURITY & INTEGRITY GUARDRAILS
## TG KindSync Pro (Enterprise Master Edition v15.0)

---

## 1. Absolute Golden Rule (Non-Negotiable)
> **PROTECT THE WORKING PROGRAM AT ALL COSTS.**  
> Existing functionality has priority over theoretical improvements.  
> Existing stability has priority over aggressive optimization.  
> Existing compatibility has priority over unnecessary architecture changes.  
> Never break what is already functional.

---

## 2. Deployment & Git Push Policy
* **Rule 2.1 (Strict Local Verification First):** All fixes, refactors, tests, and enhancements must be verified strictly on local environment first.
* **Rule 2.2 (No Automatic Remote Pushes):** NEVER automatically push commits to GitHub (`git push`) or deploy to Oracle Cloud VPS (`ssh/scp/rsync`) without explicit, direct user instruction (e.g., *"push karo"*, *"deploy karo"*, *"update deploy kar do"*).

---

## 3. Permanent Master Admin Telegram Accounts
The user has strictly and only two personal main Telegram accounts:
* **Primary 1:** `@Kinddoctor4u` (ID: `1553619403`)
* **Primary 2:** `@Ammitrajput1` (ID: `759038032`)

**Rule 3.1:** All master admin alerts, live support relays, emergency kill switches, and telemetry reports must always route strictly to these two accounts. No other accounts belong to the user.

---

## 4. Permanent Backup, Snapshot & File Export Naming Rules
Whenever generating, creating, saving, or exporting backups, database snapshots, archive packages, or telemetry reports:
* **Standard File Pattern:**  
  `[prefix]_[Day]_[Date]-[Month]-[Year]_[Time-12hAM-PM].[ext]`  
  *Example:* `history_core_backup_Sunday_13-September-2026_05-22AM.sqlite`  
  *Example:* `TG_KindSync_Pro_Friend_Edition_Monday_21-September-2026_12-24AM.zip`
* **Standard Display / Caption Pattern:**  
  `[Day], [Date] [Month] [Year] | [HH]:[MM] [AM/PM]`  
  *Example:* `Sunday, 13 September 2026 | 05:22 AM`

---

## 5. Autonomous Free AI Model Orchestration
The agent is authorized to autonomously use local free model providers in the background:
* **For Coding & Audits:** Run fast background cross-verification via **Mistral Codestral** (`python -m free_ai_hub.cli query --category coding ...`).
* **For Boilerplate & Rapid Drafting:** Use **Groq** (`python -m free_ai_hub.cli query --category fast ...`).
* **For Architecture Strategy:** Run **AI Council Debate** (`python -m free_ai_hub.cli council ...`) across multiple models (Groq + Mistral + Gemini + OpenRouter).
* **Communication:** Always communicate with the user in natural, friendly Roman Hinglish.

---

## 6. AyuGram / Eugram Strict Brand Exclusion
* **Rule 6.1:** `TG KindSync Pro` has zero affiliation with AyuGram/Eugram.
* **Rule 6.2:** All codebases, documentation, graphs, descriptions, and comments must remain 100% free of AyuGram/Eugram references. Official branding is strictly **TG KindSync Pro (Kind Doctor & Team)**.

---

## 7. Multi-Tenant Friend Edition Isolation
* **Rule 7.1:** The Friend instance (`/home/ubuntu/TG_KindSync_Friend`) must remain 100% isolated from the Admin instance.
* **Rule 7.2:** Friend workspaces must NEVER contain or inherit Admin session files (`session_forwarder.session`, `session_account2.session`) or Admin database history.
