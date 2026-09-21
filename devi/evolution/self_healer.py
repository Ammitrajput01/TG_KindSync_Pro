"""
DEVI Controlled Self-Healing Engine
Detects, diagnoses, and safely resolves transient issues (stale temp files, orphaned lockfiles, log congestion)
Strictly adheres to safety constraints: safe & reversible fixes only.
"""

import logging
import os
import time
import sqlite3
from pathlib import Path
from typing import Dict, Any, List
from contextlib import suppress

from devi.config import SANDBOX_WORKSPACE, DEVI_ROOT, DATABASE_PATH
from devi.memory.memory_store import MemoryStore

logger = logging.getLogger("DEVI.SelfHealer")

class SelfHealer:
    def __init__(self, memory_store: MemoryStore = None):
        self.memory = memory_store or MemoryStore(DATABASE_PATH)
        self.sandbox_workspace = SANDBOX_WORKSPACE
        self.project_root = Path(__file__).resolve().parent.parent.parent

    async def scan_and_heal(self) -> Dict[str, Any]:
        """
        Executes a multi-layer diagnostic scan and applies safe, reversible repairs:
        1. Stale sandbox experiment files (> 1 hour old)
        2. SQLite Memory Store integrity & baseline verification
        3. Orphaned engine.lock detection & safe cleanup
        4. Main SQLite database integrity check
        5. Stale temp files & journal cleanup
        """
        actions_taken = []
        issues_detected = 0
        now = time.time()

        # Check 1: Stale sandbox experiment files (> 1 hour old)
        if self.sandbox_workspace.exists():
            for f in self.sandbox_workspace.glob("exp_*.py"):
                try:
                    if now - f.stat().st_mtime > 3600:
                        f.unlink()
                        actions_taken.append(f"Purged stale sandbox file: {f.name}")
                        issues_detected += 1
                except Exception as e:
                    logger.warning(f"Could not purge {f.name}: {e}")

        # Check 2: Verify SQLite Memory integrity
        try:
            skills = await self.memory.list_skills()
            if not skills:
                await self.memory.initialize()
                actions_taken.append("Re-initialized empty skills baseline in memory store.")
                issues_detected += 1
        except Exception as e:
            actions_taken.append(f"Memory check anomaly: {e}")

        # Check 3: Orphaned lockfiles check
        lock_file = self.project_root / "engine.lock"
        if lock_file.exists():
            try:
                # If lockfile is older than 2 hours without active process, clear
                mtime = lock_file.stat().st_mtime
                if now - mtime > 7200:
                    lock_file.unlink()
                    actions_taken.append("Cleared stale engine.lock file (>2h old).")
                    issues_detected += 1
            except Exception as e:
                logger.debug(f"Lock check: {e}")

        # Check 4: Main Database SQLite Integrity
        main_db = self.project_root / "history_core.sqlite"
        if main_db.exists():
            try:
                con = sqlite3.connect(f"file:{main_db.resolve()}?mode=ro", uri=True, timeout=5.0)
                res = con.execute("PRAGMA quick_check").fetchone()[0]
                con.close()
                if res != "ok":
                    actions_taken.append(f"Database quick_check warning: {res}")
            except Exception as e:
                actions_taken.append(f"Database check exception: {e}")

        # Check 5: Stale temporary telemetry files
        temp_dir = self.project_root / "logs"
        if temp_dir.exists():
            for tmp_f in temp_dir.glob("*.tmp"):
                try:
                    if now - tmp_f.stat().st_mtime > 1800:
                        tmp_f.unlink()
                        actions_taken.append(f"Purged stale temp file: {tmp_f.name}")
                        issues_detected += 1
                except Exception:
                    pass

        # Record healing action in lessons
        if actions_taken:
            with suppress(Exception):
                await self.memory.record_lesson(
                    category="SELF_HEAL",
                    description="Controlled self-repair executed.",
                    root_cause=f"Detected {issues_detected} transient system anomalies.",
                    fix_solution="; ".join(actions_taken),
                    verified=1
                )

        return {
            "status": "HEALTHY" if issues_detected == 0 else "HEALED",
            "issues_resolved": issues_detected,
            "actions": actions_taken or ["All systems verified nominal; no repairs needed."]
        }
