---
name: self-extending-engine
description: Dynamic capability expansion engine for Antigravity. Use when teaching the agent new tools, creating runtime Python MCP tools, generating new reusable skills, or registering autonomous workflows into the system vault.
---

# ⚡ Antigravity Self-Extending Capability Engine

This skill guides the autonomous creation and permanent integration of new tools, scripts, and skills into Antigravity so that any model can expand its own capabilities on the fly.

---

## 1. When to Trigger Self-Extension
Trigger this skill whenever:
- A new task requires a method or tool not currently available in the default toolset.
- A procedure or workflow has been executed successfully and should be permanently preserved as a reusable runbook.
- The user asks to "teach", "learn", "add a method", or "integrate a new feature".

---

## 2. Dynamic Tool Creation (MCP Method)
When a task needs an executable method (e.g. custom API fetcher, binary patcher, DB cleaner):

1. **Invoke `dynamic_tool_forge`** via the `antigravity-omni` MCP server:
   - Provide `tool_name` (snake_case, e.g. `parse_custom_telemetry`).
   - Provide `tool_description` explaining arguments and expected return format.
   - Provide `python_code` (self-contained Python script).
2. The tool is automatically compiled, validated for syntax errors, and saved to:
   ```text
   C:\Users\Ammit\.gemini\config\tools\antigravity_omni\dynamic_tools\<tool_name>.py
   ```
3. Once created, the tool remains permanently callable across all future sessions.

---

## 3. Skill Generation & Registration (Procedure Method)
When teaching the agent a new engineering workflow or pattern:

1. Create a dedicated skill directory:
   ```text
   C:\Users\Ammit\.gemini\config\skills\<skill-name>/SKILL.md
   ```
2. Include YAML frontmatter:
   ```yaml
   ---
   name: <skill-name>
   description: <Clear 1-2 sentence summary of what the skill does and when to activate it>
   ---
   ```
3. Structure the markdown with:
   - Prerequisites & Environment.
   - Step-by-step execution protocol.
   - Verification and safety checks.
4. Run `python C:\Users\Ammit\.gemini\config\scripts\sync_agent_intelligence.py` to index the skill into the global capability registry.

---

## 4. Verification Check
- After creating a tool or skill, verify its discovery using `skill_recommender` or tool verification.
- Document the newly added capability in `memory/feature-history.md`.
