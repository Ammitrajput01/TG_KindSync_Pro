-- DEVI Structured Memory Schema
-- Phase 1: Skills, Lessons, Benchmarks, Proposals, and Dialogue

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    purpose TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('DISCOVERED', 'RESEARCHED', 'TESTED', 'VERIFIED', 'PROPOSED', 'ACTIVE', 'DEPRECATED')),
    version TEXT DEFAULT '1.0.0',
    risk_level TEXT CHECK(risk_level IN ('GREEN', 'YELLOW', 'RED')),
    learned_details TEXT,
    dependencies TEXT,
    test_plan TEXT,
    rollback_plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    root_cause TEXT,
    fix_solution TEXT,
    verified INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    benchmark_name TEXT NOT NULL,
    score REAL NOT NULL,
    max_score REAL NOT NULL,
    execution_time_ms REAL,
    details_json TEXT,
    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS upgrade_proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    benefit TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    resource_cost TEXT,
    rollback_plan TEXT,
    status TEXT NOT NULL CHECK(status IN ('PENDING', 'APPROVED', 'REJECTED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    decided_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    model_used TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
