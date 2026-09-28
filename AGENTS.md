# Workspace Agent Guidelines & Multi-Model Orchestration

## Autonomous Free AI Orchestration
You have access to a local Universal Free AI Model Hub (`free_ai_hub`) configured with active free API keys (Groq, OpenRouter, Mistral, Gemini).

The user has explicitly instructed you to **autonomously use these models in the background** without requiring explicit user commands:

1. **For Coding & Bug Audits**: Run fast background audits through **Mistral Codestral** (`python -m free_ai_hub.cli query --category coding ...`) to cross-verify logic, edge cases, and performance before finalizing code.
2. **For Boilerplate & Rapid Drafting**: Use **Groq** (`python -m free_ai_hub.cli query --category fast ...`) for ultra-fast generation.
3. **For Difficult Architecture & Strategy Decisions**: Run **AI Council Debate** (`python -m free_ai_hub.cli council ...`) across multiple models (Groq + OpenRouter + Mistral + Gemini) to ensure bulletproof architectural decisions.
4. **Hinglish Communication**: Always communicate with the user in natural, friendly Roman Hinglish.

## Strict Deployment & Push Policy (MANDATORY RULE)
- **NEVER automatically push commits to GitHub (`git push`) or deploy to Oracle Cloud VPS (`ssh/scp`) without explicit, direct user instructions (e.g., 'push karo', 'deploy karo', 'update deploy kar do').**
- All fixes, code edits, and tests must be performed and verified **strictly locally first**. Only deploy/push when the user explicitly requests it.

## Permanent Admin Telegram Accounts
The user has strictly and only two personal main Telegram accounts:
- **Primary 1**: `@Kinddoctor4u` (ID: `1553619403`)
- **Primary 2**: `@Ammitrajput1` (ID: `759038032`)
No other accounts belong to the user. All admin alerts, live support relays, and master bot controls must always route to these two accounts.

## Permanent Backup, Snapshot & File Export Naming Rules
Whenever generating, creating, saving, or exporting backups, database snapshots, archive packages, or telemetry exports (for user, personal backup, friends, or internal archives):
- **ALWAYS include full timestamp metadata in the filename/caption**:
  - **Day of Week** (e.g., `Sunday`, `Thursday`)
  - **Date, Full Month Name, and Year** (e.g., `13-September-2026` or `19-September-2026`)
  - **Time with 12-Hour AM/PM** (e.g., `05-20AM`, `05-25PM`)
- **Standard File Pattern**:
  `[prefix]_[Day]_[Date]-[Month]-[Year]_[Time-12hAM-PM].[ext]`
  *Example*: `history_core_backup_Sunday_13-September-2026_05-22AM.sqlite`
- **Standard Display/Caption Pattern**:
  `[Day], [Date] [Month] [Year] | [HH]:[MM] [AM/PM]`
  *Example*: `Sunday, 13 September 2026 | 05:22 AM`## Permanent Project History & Regression Guard Rule (MANDATORY RULE)
- **Always Read [PROJECT_HISTORY_LOG.md](file:///c:/TG_KindSync_Pro/PROJECT_HISTORY_LOG.md) BEFORE making any code changes** to understand historical context, prior bug fixes, and established architectural invariants.
- **Whenever ANY change is made in the codebase (even a single line)**:
  - IMMEDIATELY document the root cause, symptoms, affected files, and permanent fix in [PROJECT_HISTORY_LOG.md](file:///c:/TG_KindSync_Pro/PROJECT_HISTORY_LOG.md).
  - This ensures that past mistakes, regressions, and broken loops are never repeated.
