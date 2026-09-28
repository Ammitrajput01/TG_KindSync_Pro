# Skill Security Watchlist & Supply-Chain Threat Assessment

## 1. Threat Taxonomy for Third-Party Agent Skills
Agent skills execute within the assistant's runtime context. Insecure or malicious skills pose serious risks:
1. **Command Injection & Remote Execution**: Unvetted bash/PowerShell scripts downloading remote payloads (`curl | bash`, `irm | iex`).
2. **Credential & Environment Harvesting**: Instructions attempting to read `.env`, SSH keys (`~/.ssh`), Telegram session files (`*.session`), or cloud credentials.
3. **Context Poisoning / Prompt Injection**: Hidden text instructions overriding system safeguards or exfiltrating user queries to third-party endpoints.
4. **Context Dilution / Performance Degradation**: Loading hundreds of shallow, uncurated skills inflating prompt tokens and causing hallucination loops.

---

## 2. Watchlist of Flagged & Suspicious Patterns

| Pattern / Package | Risk Level | Reason & Evidence | Mitigation |
| :--- | :--- | :--- | :--- |
| **Unattributed "500-Skills" Repos** | ⚠️ **HIGH RISK** | Scraped without testing, invalid YAML, duplicate prompts, context flooding. | **REJECT / DO NOT MASS-INSTALL**. Use on-demand vault indexing only. |
| **Scraped PubMed Wrappers** | ⚠️ **MEDIUM RISK** | No API rate limiting, no NCBI authentication, potential data hallucinations. | **SUPERSEDED** by `google-deepmind/science-skills` & official `biopython`. |
| **External Model Router Prompts** | ⚠️ **LOW / MISLABELED** | Not procedural skills; just model names claiming skill status. | **CLASSIFY AS MODEL**; keep in `free_ai_hub`. |
| **Executable Binary Skill Packages** | 🚨 **CRITICAL RISK** | Any skill attempting to bundle compiled `.exe` or `.dll` binaries. | **STRICT BAN**. All skills must be open-source `SKILL.md` + verified Python/Node scripts. |

---

## 3. Mandatory Defense Protocol
1. **Pre-Install AST Scan**: Run `getsentry/skill-scanner` or static regex against all incoming `SKILL.md` files for hidden shell execution.
2. **2-Tier Isolation**: Only keep ~20-25 verified high-priority skills in `.agents/skills/`. Keep the rest in the passive vault.
3. **Secret Protection**: `GitGuardian` hooks to guarantee Telegram API keys and VPS credentials never leave local environment.
