import os
import shutil
from pathlib import Path

def setup_claude_code():
    home_dir = Path.home()
    claude_dir = home_dir / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    
    plugins_dir = claude_dir / "plugins"
    plugins_dir.mkdir(parents=True, exist_ok=True)
    
    skills_dir = claude_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    
    commands_dir = claude_dir / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Copy plugins & skills from .gemini to .claude
    gemini_plugins = home_dir / ".gemini" / "config" / "plugins"
    if gemini_plugins.exists():
        for item in gemini_plugins.iterdir():
            target_path = plugins_dir / item.name
            try:
                if item.is_dir():
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(item, target_path)
                else:
                    shutil.copy2(item, target_path)
            except Exception as e:
                print(f"Skipping {item.name}: {e}")
        print(f"Synced plugins from {gemini_plugins} to {plugins_dir}")

    # 2. Write global CLAUDE.md
    claude_md_path = claude_dir / "CLAUDE.md"
    claude_md_content = """# CLAUDE CODE — SUPREME AGENTIC CONFIGURATION

## 1. Token Optimization & Context Efficiency (CRITICAL)
- Minimize token usage by keeping responses dense, actionable, and concise.
- Never output full files when only a small diff is needed.
- Use ripgrep / AST graph queries instead of bulk file reads.
- Always check local AST graphs before scanning broad directories.

## 2. Autonomous Free AI Model Hub Orchestration
- You have access to the local PC Universal Free AI Hub (`free_ai_hub`):
  - **Fast Boilerplate / Drafting**: Groq (`python -m free_ai_hub.cli query --category fast ...`)
  - **Deep Code Audits**: Mistral Codestral (`python -m free_ai_hub.cli query --category coding ...`)
  - **Complex Decisions**: AI Council Debate (`python -m free_ai_hub.cli council ...`)

## 3. Strict Safety & Push Policy
- NEVER automatically push commits (`git push`) or deploy to Oracle Cloud VPS without explicit user instructions.
- All code edits must be verified locally with test suites first (`pytest tests/`).

## 4. Permanent Master Admin Telegram Accounts
- Primary 1: `@Kinddoctor4u` (ID: `1553619403`)
- Primary 2: `@Ammitrajput1` (ID: `759038032`)

## 5. Standard Backup Naming Rule
- Pattern: `[prefix]_[Day]_[Date]-[Month]-[Year]_[Time-12hAM-PM].[ext]`
- Display: `[Day], [Date] [Month] [Year] | [HH]:[MM] [AM/PM]`

## 6. Language & Tone
- Always communicate with the user in warm, natural Roman Hinglish.
"""
    claude_md_path.write_text(claude_md_content, encoding="utf-8")
    print(f"Created master global CLAUDE.md at: {claude_md_path}")
    
    # 3. Also copy CLAUDE.md to current project root
    project_claude_md = Path("C:/TG_KindSync_Pro/CLAUDE.md")
    project_claude_md.write_text(claude_md_content, encoding="utf-8")
    print(f"Created project CLAUDE.md at: {project_claude_md}")

    print("\nSUCCESS: Claude Code environment is 100% configured and supercharged!")

if __name__ == "__main__":
    setup_claude_code()
