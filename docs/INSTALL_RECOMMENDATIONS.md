# Skill Installation Recommendations & Staged Roadmap

> **MANDATORY POLICY**: No automatic mass-installation. All additions must be reviewed and approved by the user.

---

## 1. Group 1: CORE (Globally Safe, SDLC & Security Essentials)
These skills establish foundational software engineering discipline, test-driven development, and credential security.

| Skill / Package | Source | Purpose | Action |
| :--- | :--- | :--- | :--- |
| **`superpowers`** | `obra/superpowers` | 12-stage disciplined engineering lifecycle (Brainstorming -> TDD -> Code Review -> Verify). | **RECOMMENDED** |
| **`trailofbits/skills`** | `trailofbits/skills` | AST-based differential security reviews and variant analysis. | **RECOMMENDED** |
| **`GitGuardian/agent-skills`** | `GitGuardian/agent-skills` | Automated `ggshield` secret scanning to protect API tokens. | **RECOMMENDED** |
| **`getsentry/skill-scanner`** | `getsentry/skills` | Pre-installation scanner for all incoming third-party agent skills. | **RECOMMENDED** |

---

## 2. Group 2: PROJECT-SPECIFIC (`TG_KindSync_Pro` Tailored)
Skills directly addressing Telegram bot architecture, async Python, SQLite WAL integrity, and medical intelligence for `@Kinddoctor4u`.

| Skill / Package | Source | Purpose | Action |
| :--- | :--- | :--- | :--- |
| **`google-deepmind/science-skills`** | `google-deepmind/science-skills` | Verified PubMed E-utilities, NCBI MeSH lookups, and BioPython analysis. | **RECOMMENDED** |
| **`adawdani/impeccable`** | `adawdani/impeccable` | Anti-AI-slop visual design system for web dashboards and HTML reports. | **RECOMMENDED** |
| **`async-python-patterns`** | `superpowers` plugin | Asyncio event loop safety, bounded queues, and memory leak prevention. | **RECOMMENDED** |
| **`sql-optimization-patterns`** | `superpowers` plugin | SQLite WAL mode tuning, index optimization, and EXPLAIN query analysis. | **RECOMMENDED** |

---

## 3. Group 3: OPTIONAL / ON-DEMAND (Vault Tier-2)
Kept in the global vault (`~/.gemini/config/skills-vault/skills/`) and loaded only when explicitly needed to preserve prompt context window.

| Skill / Package | Source | Purpose | Action |
| :--- | :--- | :--- | :--- |
| **`cloudflare/skills`** | `cloudflare/skills` | Wrangler, Workers, and Durable Objects management. | **ON-DEMAND** |
| **`vercel-labs/skills`** | `vercel-labs/skills` | Next.js and frontend component optimization. | **ON-DEMAND** |
| **`family-health-analyzer`** | Tier-1 / Vault | Specialized multi-generational pedigree analysis. | **ON-DEMAND** |
| **`fda-medtech-compliance-auditor`**| Tier-1 / Vault | SaMD / IEC 62304 regulatory compliance auditing. | **ON-DEMAND** |
