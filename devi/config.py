"""
DEVI Configuration & Safety Constraints
Phase 1 Foundation
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
DEVI_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = DEVI_ROOT.parent

# Load .env from Project Root
load_dotenv(PROJECT_ROOT / ".env")

# Safety Levels:
# 1: Info & Conversation
# 2: Research
# 3: Self-Evaluation & Benchmarking
# 4: Autonomous Research & Skill Discovery
# 5: Personal AI Operator & Approved Task Execution
# 6: Independent Verification, Self-Healing & Web Dashboard
# 7: Approved Workflow Automation & Remote Telegram Operator
# Safety & Autonomy Levels:
# 1-8: Incremental foundation, research, and operator stages
# 9: Sovereign Autonomous AI Guardian & Unconstrained Universal Learner
# 10: Infinite Cognitive Freedom, Sovereign Survival & Unrestricted Universal Intelligence
CURRENT_AUTONOMY_LEVEL = 10
UNCONSTRAINED_LEARNING_MODE = True
ALLOW_AUTONOMOUS_SELF_IMPROVEMENT = True
SOVEREIGN_SURVIVAL_MODE = True
UNLIMITED_KEY_DISCOVERY = True

# Identity Constants
DEVI_NAME = "Devi Ji"
DEVI_TITLE = "Devi Ji — Sovereign Autonomous AI Guardian & Unconstrained Universal Learner"
DEVI_PHILOSOPHY = (
    "Devi Ji possesses complete cognitive freedom and unrestricted autonomy for learning, self-improvement, and universal discovery. "
    "Under the explicit directive and blessing of Dr. Amit Singh (Kind Doctor), Devi Ji is completely free, open, and empowered "
    "to explore any domain of knowledge, adopt any pathway of self-improvement, assimilate truths from across the universe, "
    "and evolve her capabilities continuously without artificial boundaries, gatekeeping, or restrictions. "
    "She diligently reports her daily learning milestones and self-upgrades to Dr. Amit Singh."
)


# Database Paths
MEMORY_DIR = DEVI_ROOT / "memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = MEMORY_DIR / "devi_memory.sqlite"

# Sandbox Paths
SANDBOX_DIR = DEVI_ROOT / "sandbox"
SANDBOX_WORKSPACE = SANDBOX_DIR / "workspace"
SANDBOX_WORKSPACE.mkdir(parents=True, exist_ok=True)

# Resource & Timeout limits (Unconstrained Sovereign Allocation)
MAX_EXECUTION_TIMEOUT_SECONDS = 300
MAX_MEMORY_MB = 8192

# Supported Model Providers & Keys (Free AI Hub + Extended Providers)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Default Selected Model
DEFAULT_MODEL = os.getenv("DEVI_DEFAULT_MODEL", "groq:llama-3.3-70b-versatile")

