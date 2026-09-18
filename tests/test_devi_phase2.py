"""
DEVI Phase 2 Verification Suite
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from devi.memory.memory_store import MemoryStore
from devi.brain.model_router import ModelRouter
from devi.research.research_agent import ResearchAgent
from devi.skills.discovery import SkillDiscoveryEngine
from devi.skills.tester import SkillTester

async def run_phase2_verification():
    print("========================================")
    print("   DEVI PHASE 2 VERIFICATION SUITE")
    print("========================================")

    # 1. Initialize Memory Store
    print("[*] 1. Initializing Memory Store...")
    mem = MemoryStore()
    await mem.initialize()
    print("    [+] Memory store ready.")

    # 2. Test Research Agent
    print("[*] 2. Testing Research Agent topic synthesis...")
    router = ModelRouter()
    researcher = ResearchAgent(router)
    res_data = await researcher.research_topic("SQLite WAL mode optimization for concurrent writes")
    assert "topic" in res_data and len(res_data["report"]) > 0, "Research synthesis failed"
    print(f"    [+] Research report generated via '{res_data['provider']}' ({res_data['elapsed_ms']:.2f} ms).")

    # 3. Test Skill Discovery
    print("[*] 3. Testing Skill Discovery Engine...")
    discovery = SkillDiscoveryEngine(mem)
    skill_name = "test_phase2_skill"
    test_code = "print('PHASE2_SKILL_OK')"
    disc_res = await discovery.discover_skill(
        name=skill_name,
        purpose="Verify Phase 2 dynamic lifecycle",
        benefit="Automated discovery pipeline",
        risk_level="GREEN",
        test_script=test_code
    )
    assert disc_res["status"] == "DISCOVERED"
    print(f"    [+] Skill '{skill_name}' registered as DISCOVERED.")

    # 4. Test Skill Sandbox Testing & Proposal Generation
    print("[*] 4. Testing Skill Tester in Isolated Sandbox...")
    tester = SkillTester(mem)
    test_res = await tester.test_and_propose_skill(
        name=skill_name,
        test_code=test_code,
        benefit="Automated verification test",
        risk_level="GREEN",
        resource_cost="Minimal"
    )
    assert test_res["verified"] is True
    assert test_res["status"] == "TESTED"
    print(f"    [+] Skill tested in sandbox ({test_res['elapsed_ms']:.2f} ms) -> Proposal #{test_res['proposal_id']} created.")

    # 5. Test Proposal Approval Mechanism
    print("[*] 5. Testing Human-In-The-Loop Approval...")
    pending = await mem.get_pending_proposals()
    target_proposal = [p for p in pending if p["id"] == test_res["proposal_id"]]
    assert len(target_proposal) == 1, "Proposal not found in pending list"
    
    # User Approves
    await mem.decide_proposal(test_res["proposal_id"], "APPROVED")
    await mem.update_skill_status(skill_name, "ACTIVE")
    
    active_skills = await mem.list_skills(status="ACTIVE")
    active_names = [s["name"] for s in active_skills]
    assert skill_name in active_names, "Skill should now be ACTIVE after user approval"
    print(f"    [+] User approved proposal -> Skill '{skill_name}' is now ACTIVE.")

    print("\n[OK] ALL DEVI PHASE 2 TESTS PASSED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_phase2_verification())
