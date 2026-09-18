"""
DEVI Intent Engine
Parses user intent, detects commands vs casual talk, and decomposes tasks.
"""

from typing import Dict, Any

class IntentEngine:
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        text = user_input.strip().lower()

        # Check for benchmark / self eval
        if any(w in text for w in ["benchmark", "self eval", "test yourself", "evaluate yourself", "eval"]):
            return {"intent": "RUN_BENCHMARK", "raw": user_input}

        # Check for research command
        if text.startswith("research "):
            topic = user_input[len("research "):].strip()
            return {"intent": "RESEARCH_TOPIC", "topic": topic}
        elif "research " in text:
            # e.g. "devi, research telegram rate limits"
            parts = user_input.split("research ", 1)
            return {"intent": "RESEARCH_TOPIC", "topic": parts[1].strip()}

        # Check for discover skills
        if any(w in text for w in ["discover skills", "find new skills", "search skills", "learn new"]):
            return {"intent": "DISCOVER_SKILLS", "raw": user_input}

        # Check for system health / diagnostics
        if any(w in text for w in ["health", "ram", "cpu", "memory", "system status", "diagnostics"]):
            return {"intent": "CHECK_HEALTH", "raw": user_input}



        # Check for inspect logs / errors
        if any(w in text for w in ["logs", "check logs", "errors", "check errors", "check error", "recent errors", "tail log", "kya error", "koi error", "dlq"]):
            return {"intent": "INSPECT_LOGS", "raw": user_input}

        # Check for search files
        if text.startswith("find ") or text.startswith("search file "):
            pattern = user_input.split(" ", 1)[1].strip()
            return {"intent": "SEARCH_FILES", "pattern": pattern}

        # Check for skills list
        if any(w in text for w in ["skills", "capabilities", "kya kar sakti ho", "what can you do"]):
            return {"intent": "LIST_SKILLS", "raw": user_input}

        # Check for proposals
        if any(w in text for w in ["proposals", "upgrades", "pending upgrades"]):
            return {"intent": "VIEW_PROPOSALS", "raw": user_input}

        if text.startswith("approve "):
            try:
                pid = int(text.split("approve ")[1].strip())
                return {"intent": "APPROVE_PROPOSAL", "proposal_id": pid}
            except ValueError:
                pass

        if text.startswith("reject "):
            try:
                pid = int(text.split("reject ")[1].strip())
                return {"intent": "REJECT_PROPOSAL", "proposal_id": pid}
            except ValueError:
                pass

        # Check for kill processes / terminate / unlock database
        if any(w in text for w in ["kill", "killall", "kill all", "kill python", "force stop", "stop all", "unlock db", "database lock", "database is locked", "db unlock", "kill karo", "band karo", "process kill", "stuck ho gya", "stuck ho gaya", "terminate"]):
            return {"intent": "KILL_PROCESSES", "raw": user_input}

        # Check for clean history / reset forwarding records
        if any(w in text for w in ["clean history", "clear history", "reset history", "wipe history", "purge history", "delete history", "history clean", "history clear", "history delete", "history saaf", "history reset", "history mita", "history wipe", "saaf karo history"]):
            return {"intent": "CLEAN_HISTORY", "raw": user_input}

        # Check for status / speed / progress / kya ho rha hai
        if any(w in text for w in ["status", "level", "autonomy", "speed", "velocity", "progress", "forwarding", "kya ho rha", "kya ho raha", "kya chal rha", "kya chal raha", "kaisa chal", "kaisi chal", "update", "kya update", "sab theek"]):
            return {"intent": "SHOW_STATUS", "raw": user_input}

        # Default is dialogue / chat
        return {"intent": "CONVERSATION", "raw": user_input}

