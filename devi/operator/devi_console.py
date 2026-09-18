"""
DEVI Interactive Console
Natural Language Interactive Interface for DEVI (AI Teacher & Future Operator)
"""

import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from devi.config import DEVI_NAME, DEVI_TITLE, CURRENT_AUTONOMY_LEVEL
from devi.memory.memory_store import MemoryStore
from devi.brain.model_router import ModelRouter
from devi.brain.context_engine import ContextEngine
from devi.brain.intent_engine import IntentEngine
from devi.evolution.evaluator import Evaluator
from devi.evolution.upgrade_proposal import UpgradeProposalGenerator
from devi.research.research_agent import ResearchAgent
from devi.skills.discovery import SkillDiscoveryEngine
from devi.skills.tester import SkillTester
from devi.operator.task_executor import TaskExecutor
from devi.operator.telegram_bridge import TelegramBridge
from devi.brain.agent_loop import AgentLoop

console = Console()

class DeviConsole:
    def __init__(self):
        self.memory = MemoryStore()
        self.router = ModelRouter()
        self.context_engine = ContextEngine(self.memory)
        self.intent_engine = IntentEngine()
        self.evaluator = Evaluator(self.memory)
        self.proposal_gen = UpgradeProposalGenerator(self.memory)
        self.researcher = ResearchAgent(self.router)
        self.discovery = SkillDiscoveryEngine(self.memory)
        self.tester = SkillTester(self.memory)
        self.executor = TaskExecutor(self.memory)
        self.telegram_bridge = TelegramBridge()
        self.agent_loop = AgentLoop(self.memory, self.router)
        self.session_id = "devi_cli_session_1"

    async def start(self):
        await self.memory.initialize()
        self._show_banner()

        while True:
            try:
                user_input = console.input("\n[bold cyan]User > [/bold cyan]").strip()
                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit", "bye"]:
                    console.print("\n[bold magenta]DEVI:[/bold magenta] Goodbye! Staying vigilant and continuing to learn.\n")
                    break

                await self._process_input(user_input)

            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold magenta]DEVI:[/bold magenta] Session terminated safely.\n")
                break
            except Exception as e:
                console.print(f"[bold red][!] Error: {e}[/bold red]")

    def _show_banner(self):
        providers = [k for k, v in self.router.available_providers.items() if v]
        provider_str = ", ".join(providers) if providers else "Local Offline Core"

        content = (
            f"[bold yellow]{DEVI_NAME}[/bold yellow] - [bold white]{DEVI_TITLE}[/bold white]\n"
            f"[dim]Autonomy Level: {CURRENT_AUTONOMY_LEVEL}/9 (Personal AI Operator & Task Execution)[/dim]\n"
            f"[dim]Active Models / Providers: {provider_str}[/dim]\n"
            f"[dim]Safe Sandbox: Enabled | TGForwarder Isolated & Protected[/dim]\n\n"
            f"[cyan]Quick Commands:[/cyan] 'health', 'find <pattern>', 'logs', 'research <topic>', 'discover skills', 'benchmark', 'status', 'exit'"
        )
        console.print(Panel(content, title="[bold green]DEVI AI SYSTEM[/bold green]", border_style="cyan"))

    async def _process_input(self, user_input: str):
        parsed = self.intent_engine.parse_intent(user_input)
        intent = parsed["intent"]

        if intent == "SHOW_STATUS":
            await self._display_status()
        elif intent == "LIST_SKILLS":
            await self._display_skills()
        elif intent == "RUN_BENCHMARK":
            await self._run_benchmark()
        elif intent == "CHECK_HEALTH":
            await self._handle_system_health()
        elif intent == "INSPECT_LOGS":
            await self._handle_inspect_logs()
        elif intent == "SEARCH_FILES":
            await self._handle_search_files(parsed["pattern"])
        elif intent == "RESEARCH_TOPIC":
            await self._handle_research(parsed["topic"])
        elif intent == "DISCOVER_SKILLS":
            await self._handle_skill_discovery()
        elif intent == "VIEW_PROPOSALS":
            await self._display_proposals()
        elif intent == "APPROVE_PROPOSAL":
            await self._handle_proposal_decision(parsed["proposal_id"], "APPROVED")
        elif intent == "REJECT_PROPOSAL":
            await self._handle_proposal_decision(parsed["proposal_id"], "REJECTED")
        else:
            # Check if user gave a compound task (e.g. contains 'check' and 'find' or multiple intents)
            user_lower = user_input.lower()
            if any(w in user_lower for w in ["check", "find", "search", "inspect", "summarize", "smoothly"]) and len(user_input.split()) > 3:
                with console.status("[bold magenta]DEVI Agent Planning & Executing Multi-Step Goal...[/bold magenta]", spinner="dots"):
                    loop_res = await self.agent_loop.run_compound_task(user_input)
                console.print(f"\n[bold magenta]DEVI (Autonomous Operator):[/bold magenta]\n{loop_res['final_summary']}")
                await self.memory.append_conversation(self.session_id, "user", user_input)
                await self.memory.append_conversation(self.session_id, "devi", loop_res['final_summary'], model_used="DEVI-AgentLoop")
                return

            # Normal Multi-model Conversation Flow
            with console.status("[bold magenta]DEVI is thinking...[/bold magenta]", spinner="dots"):
                system_prompt = await self.context_engine.build_system_prompt()
                history = await self.memory.get_recent_history(self.session_id, limit=6)
                res = await self.router.generate_response(system_prompt, user_input, history)

            await self.memory.append_conversation(self.session_id, "user", user_input)
            await self.memory.append_conversation(self.session_id, "devi", res["content"], model_used=res["provider"])

            header = f"[bold magenta]DEVI ({res['provider']} - {res['elapsed_ms']:.0f}ms):[/bold magenta]"
            console.print(f"\n{header}\n{res['content']}")

    async def _display_status(self):
        table = Table(title="DEVI Current State", border_style="cyan")
        table.add_column("Property", style="bold yellow")
        table.add_column("Value", style="green")

        table.add_row("Identity", DEVI_NAME)
        table.add_row("Current Role", "AI Teacher -> Self-Evaluating AI")
        table.add_row("Autonomy Level", f"Level {CURRENT_AUTONOMY_LEVEL} (Evaluation & Bounded Tooling)")
        table.add_row("Memory Store", "SQLite (devi/memory/devi_memory.sqlite)")
        table.add_row("Sandbox Isolation", "Active (devi/sandbox/workspace/)")
        
        benchmarks = await self.memory.get_latest_benchmarks(1)
        latest_score = f"{benchmarks[0]['score']}/{benchmarks[0]['max_score']}" if benchmarks else "Not run yet"
        table.add_row("Latest Benchmark", latest_score)

        console.print(table)

    async def _display_skills(self):
        skills = await self.memory.list_skills()
        table = Table(title="DEVI Skills Registry", border_style="blue")
        table.add_column("ID", justify="right", style="dim")
        table.add_column("Skill Name", style="bold cyan")
        table.add_column("Purpose", style="white")
        table.add_column("Status", style="green")
        table.add_column("Risk", style="yellow")

        for s in skills:
            table.add_row(str(s["id"]), s["name"], s["purpose"], s["status"], s["risk_level"])

        console.print(table)

    async def _handle_system_health(self):
        res = await self.executor.execute_task("CHECK_SYSTEM_HEALTH")
        health = res["health"]

        table = Table(title="DEVI System Diagnostics & Resource Telemetry", border_style="cyan")
        table.add_column("Resource / Metric", style="bold yellow")
        table.add_column("Reading", style="bold green")

        table.add_row("Status", health["status"])
        table.add_row("OS Environment", health["os"])
        table.add_row("CPU Load", f"{health['cpu_usage_pct']}%")
        table.add_row("RAM Usage", f"{health['used_ram_pct']}% ({health['available_ram_gb']} GB available / {health['total_ram_gb']} GB total)")
        table.add_row("Disk Space", f"{health['free_disk_gb']} GB free / {health['total_disk_gb']} GB total")
        table.add_row("Active Python Tasks", str(res["active_python_processes"]))

        console.print(table)

    async def _handle_inspect_logs(self):
        res = await self.executor.execute_task("INSPECT_LOGS")
        data = res.get("data", {})
        if "error" in data:
            console.print(f"[bold red][X] {data['error']}[/bold red]")
            return

        if not data.get("entries") and not data.get("tail"):
            console.print(f"[yellow][!] {data.get('status', 'No log data available.')}[/yellow]")
            return

        panel = Panel(
            data["tail"],
            title=f"[bold green]Recent Log Stream: {data['file']} (Lines: {data['total_lines']})[/bold green]",
            border_style="yellow"
        )
        console.print(panel)

    async def _handle_search_files(self, pattern: str):
        res = await self.executor.execute_task("SEARCH_FILES", {"pattern": pattern})
        matches = res.get("matches", [])

        table = Table(title=f"Search Results for '{pattern}' ({len(matches)} files found)", border_style="blue")
        table.add_column("#", justify="right", style="dim")
        table.add_column("File Path", style="bold white")

        for idx, path in enumerate(matches, 1):
            table.add_row(str(idx), path)

        console.print(table)

    async def _run_benchmark(self):
        console.print("\n[bold yellow][*] Running Foundation Self-Evaluation Suite...[/bold yellow]")
        with console.status("[bold cyan]Testing memory, sandbox, and safety boundaries...[/bold cyan]", spinner="bouncingBar"):
            result = await self.evaluator.run_foundation_benchmark()

        table = Table(title=f"Benchmark Report: {result['benchmark_name']}", border_style="green")
        table.add_column("Test Component", style="bold cyan")
        table.add_column("Status", style="bold")
        table.add_column("Score", justify="right")
        table.add_column("Details", style="dim")

        for comp, data in result["breakdown"].items():
            status_str = "[green]PASSED[/green]" if data["passed"] else "[red]FAILED[/red]"
            table.add_row(comp, status_str, f"{data['score']:.1f}", data["details"])

        console.print(table)
        console.print(f"[bold green]Total Score: {result['score']}/{result['max_score']} (Elapsed: {result['elapsed_ms']:.2f} ms)[/bold green]\n")

    async def _handle_research(self, topic: str):
        console.print(f"\n[bold yellow][*] DEVI Researching:[/bold yellow] [white]{topic}[/white]...")
        with console.status("[bold cyan]Analyzing architecture, security risks & capability gaps...[/bold cyan]", spinner="arc"):
            res = await self.researcher.research_topic(topic)

        panel = Panel(
            Markdown(res["report"]),
            title=f"[bold green]DEVI Research Report: {topic} ({res['provider']})[/bold green]",
            border_style="magenta"
        )
        console.print(panel)

    async def _handle_skill_discovery(self):
        console.print("\n[bold yellow][*] DEVI Scanning for Candidate Capabilities...[/bold yellow]")
        
        # Example candidate discovered: Advanced JSON Streaming Parser
        name = "stream_chunk_hasher"
        purpose = "Ultra-fast sha256 rolling chunk verification for downloaded files"
        benefit = "Ensures zero-corruption media streaming without loading full files into RAM."
        test_script = (
            "import hashlib\n"
            "h = hashlib.sha256()\n"
            "for chunk in [b'chunk_1', b'chunk_2', b'chunk_3']:\n"
            "    h.update(chunk)\n"
            "digest = h.hexdigest()\n"
            "assert len(digest) == 64\n"
            "print(f'DIGEST_VERIFIED:{digest[:16]}')\n"
        )

        with console.status("[bold cyan]1. Registering candidate skill in memory (DISCOVERED)...[/bold cyan]"):
            await self.discovery.discover_skill(
                name=name,
                purpose=purpose,
                benefit=benefit,
                risk_level="GREEN",
                dependencies="hashlib (standard library)",
                test_script=test_script
            )

        with console.status("[bold cyan]2. Testing candidate in isolated sandbox...[/bold cyan]"):
            test_res = await self.tester.test_and_propose_skill(
                name=name,
                test_code=test_script,
                benefit=benefit,
                risk_level="GREEN",
                resource_cost="Minimal (< 1MB RAM)"
            )

        if test_res["verified"]:
            console.print(f"[bold green][✓] Candidate Skill '{name}' successfully verified in sandbox ({test_res['elapsed_ms']:.2f}ms)![/bold green]")
            console.print(f"[bold yellow][!] Generated Upgrade Proposal #{test_res['proposal_id']} awaiting User Approval.[/bold yellow]")
            console.print("[dim]Type 'proposals' to inspect or 'approve " + str(test_res['proposal_id']) + "' to activate.[/dim]\n")
        else:
            console.print(f"[bold red][X] Sandbox verification failed: {test_res['error']}[/bold red]\n")

    async def _display_proposals(self):
        proposals = await self.memory.get_pending_proposals()
        if not proposals:
            console.print("\n[green][✓] No pending upgrade proposals. DEVI is running at the approved baseline.[/green]")
            return

        table = Table(title="Pending DEVI Self-Upgrade Proposals (User Approval Required)", border_style="yellow")
        table.add_column("ID", justify="right", style="dim")
        table.add_column("Title", style="bold yellow")
        table.add_column("Benefit", style="white")
        table.add_column("Risk", style="red")
        table.add_column("Rollback Plan", style="dim")

        for p in proposals:
            table.add_row(str(p["id"]), p["title"], p["benefit"], p["risk_level"], p["rollback_plan"])

        console.print(table)
        console.print("[dim]Use 'approve <id>' or 'reject <id>' to make a decision.[/dim]")

    async def _handle_proposal_decision(self, proposal_id: int, decision: str):
        await self.memory.decide_proposal(proposal_id, decision)
        color = "green" if decision == "APPROVED" else "red"
        console.print(f"[{color}][✓] Proposal #{proposal_id} marked as {decision}.[/color]")

def main():
    devi_app = DeviConsole()
    asyncio.run(devi_app.start())

if __name__ == "__main__":
    main()
