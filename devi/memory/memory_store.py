"""
DEVI Memory Store & Persistence
Lightweight SQLite Manager for Skills, Lessons, Benchmarks, and Proposals
"""

import aiosqlite
import json
import logging
from typing import List, Dict, Any, Optional
from devi.config import DATABASE_PATH, DEVI_ROOT

logger = logging.getLogger("DEVI.Memory")

SCHEMA_FILE = DEVI_ROOT / "memory" / "schema.sql"

class MemoryStore:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path

    async def initialize(self):
        """Creates tables from schema if not exists."""
        schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(schema_sql)
            await db.commit()
            
            # Seed default foundation skills if empty
            async with db.execute("SELECT COUNT(*) FROM skills") as cursor:
                count = (await cursor.fetchone())[0]
                if count == 0:
                    await self._seed_initial_skills(db)

    async def _seed_initial_skills(self, db):
        initial_skills = [
            ("natural_conversation", "Engage with user in natural multi-turn dialogue", "ACTIVE", "GREEN", "Foundation conversation capability"),
            ("self_eval_benchmarking", "Run internal logic, memory, and reasoning checks", "ACTIVE", "GREEN", "Phase 1 self-evaluation suite"),
            ("sandbox_code_execution", "Execute safe exploratory scripts in isolated sandbox", "ACTIVE", "GREEN", "Subprocess execution with timeout constraints"),
            ("multi_model_routing", "Query multiple AI providers with automatic fallback", "ACTIVE", "GREEN", "Unified HTTP model adapter"),
            ("upgrade_proposal_generator", "Generate formal evolution reports requiring user sign-off", "ACTIVE", "GREEN", "Human-in-the-loop protection")
        ]
        for name, purpose, status, risk, learned in initial_skills:
            await db.execute(
                """INSERT INTO skills (name, purpose, status, risk_level, learned_details) 
                   VALUES (?, ?, ?, ?, ?)""",
                (name, purpose, status, risk, learned)
            )
        await db.commit()

    async def list_skills(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT id, name, purpose, status, version, risk_level FROM skills"
        params = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY id ASC"

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def register_skill(self, name: str, purpose: str, status: str = "DISCOVERED", 
                             risk_level: str = "GREEN", learned_details: str = "",
                             dependencies: str = "", test_plan: str = "", rollback_plan: str = ""):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO skills 
                   (name, purpose, status, risk_level, learned_details, dependencies, test_plan, rollback_plan, updated_at) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (name, purpose, status, risk_level, learned_details, dependencies, test_plan, rollback_plan)
            )
            await db.commit()

    async def update_skill_status(self, name: str, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE skills SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?", (status, name))
            await db.commit()

    async def record_lesson(self, category: str, description: str, root_cause: str = "", fix_solution: str = "", verified: int = 1):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO lessons (category, description, root_cause, fix_solution, verified) 
                   VALUES (?, ?, ?, ?, ?)""",
                (category, description, root_cause, fix_solution, verified)
            )
            await db.commit()

    async def record_benchmark(self, benchmark_name: str, score: float, max_score: float, execution_time_ms: float, details: Dict[str, Any]):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO benchmarks (benchmark_name, score, max_score, execution_time_ms, details_json) 
                   VALUES (?, ?, ?, ?, ?)""",
                (benchmark_name, score, max_score, execution_time_ms, json.dumps(details))
            )
            await db.commit()

    async def get_latest_benchmarks(self, limit: int = 5) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT benchmark_name, score, max_score, execution_time_ms, run_date FROM benchmarks ORDER BY id DESC LIMIT ?",
                (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def create_upgrade_proposal(self, title: str, description: str, benefit: str, risk_level: str, resource_cost: str, rollback_plan: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """INSERT INTO upgrade_proposals (title, description, benefit, risk_level, resource_cost, rollback_plan, status) 
                   VALUES (?, ?, ?, ?, ?, ?, 'PENDING')""",
                (title, description, benefit, risk_level, resource_cost, rollback_plan)
            )
            await db.commit()
            return cursor.lastrowid

    async def get_pending_proposals(self) -> List[Dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM upgrade_proposals WHERE status = 'PENDING' ORDER BY id ASC"
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def decide_proposal(self, proposal_id: int, decision: str):
        # decision: APPROVED or REJECTED
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE upgrade_proposals SET status = ?, decided_at = CURRENT_TIMESTAMP WHERE id = ?",
                (decision, proposal_id)
            )
            await db.commit()

    async def append_conversation(self, session_id: str, role: str, content: str, model_used: str = "DEVI-Brain"):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO conversation_history (session_id, role, content, model_used) VALUES (?, ?, ?, ?)",
                (session_id, role, content, model_used)
            )
            await db.commit()

    async def get_recent_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT role, content FROM conversation_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            ) as cursor:
                rows = await cursor.fetchall()
                history = [dict(row) for row in rows]
                return history[::-1]
