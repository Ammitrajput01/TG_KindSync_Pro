# Agent Skill Intelligence Research Log

## 1. Research Protocol & Methodology
- **Objective**: Multi-round internet-scale intelligence investigation into the `SKILL.md` open agent skills ecosystem, official vendor repositories, security auditors, and community frameworks.
- **Search Strategy**: Query families across Vendor APIs, GitHub Topics, Package Registries, and Security Frameworks.
- **Date**: September 28, 2026.

---

## 2. Query Families & Investigation Rounds

### Round 1: Official Vendor Ecosystems
- **Query**: `"SKILL.md"` OR `plugin.json` in `github.com/google-deepmind`, `github.com/cloudflare`, `github.com/vercel`, `github.com/trailofbits`, `github.com/GitGuardian`, `github.com/getsentry`.
- **Findings**:
  - `google-deepmind/science-skills`: Authentic NCBI/PubMed + Biopython pipeline.
  - `trailofbits/skills`: Formal differential review, variant analysis.
  - `GitGuardian/agent-skills`: `ggshield` secret detection integration.
  - `getsentry/skills`: Pre-install AST skill scanner.
  - `cloudflare/skills`: Workers, Wrangler, Agents SDK.
  - `vercel-labs/skills`: `npx skills` official CLI and component best practices.
- **Yield**: High (6 verified vendor packages).

### Round 2: Agent Engineering Lifecycles & SDLC
- **Query**: `agent skills TDD "systematic-debugging" "verification-before-completion" "brainstorming"`.
- **Findings**:
  - `obra/superpowers`: Standardized 12-stage engineering lifecycle with subagent coordination.
  - `addyosmani/agent-skills`: 6-stage lifecycle (Define -> Plan -> Build -> Verify -> Review -> Ship).
  - `affaan-m/everything-claude-code`: 68 subagents + AgentShield security guard.
- **Yield**: Very High (Core operational standards established).

### Round 3: Visual Design & Anti-AI-Slop
- **Query**: `UI UX design skills "impeccable" "anti-slop" CSS motion`.
- **Findings**:
  - `adawdani/impeccable`: 59 deterministic visual heuristics.
  - `emil-kowalski-motion`: Spring physics & cubic-bezier micro-interaction principles.
- **Yield**: High.

### Round 4: Discarded Candidates & Dead Ends
- **Scraped / Unattributed PubMed wrappers**: Low quality, lack API key rotation and MeSH term grounding. Replaced by `google-deepmind/science-skills`.
- **Model Router Claims ("Nex-N2.5")**: External LLM inference routing models, not procedural `SKILL.md` instruction packages.
- **Mass "500-skills" dumps**: 90% duplicated or shallow single-sentence prompts without test cases or decision trees. Rejected to prevent context pollution.

---

## 3. Saturation Assessment
- **Discovery Yield**: Consecutive searches in community indexes converged on variations/forks of `obra/superpowers`, `trailofbits`, `affaan-m/ECC`, and `addyosmani`.
- **Confidence**: EXTENSIVE / HIGH CONFIDENCE.
