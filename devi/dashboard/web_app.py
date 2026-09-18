"""
DEVI Lightweight Asynchronous Web Dashboard Server
Runs locally on http://127.0.0.1:8765 using standard aiohttp (already in requirements.txt).
Consumes < 25MB RAM.
"""

import asyncio
from aiohttp import web
from pathlib import Path
from devi.config import DEVI_NAME, CURRENT_AUTONOMY_LEVEL
from devi.memory.memory_store import MemoryStore
from devi.tools.system_tools import SystemTools

DASHBOARD_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = DASHBOARD_DIR / "templates"

class DashboardApp:
    def __init__(self, port: int = 8765):
        self.port = port
        self.memory = MemoryStore()
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        self.app.router.add_get("/", self.index_handler)
        self.app.router.add_get("/api/status", self.status_api)
        self.app.router.add_get("/api/proposal/{id}/approve", self.approve_api)
        self.app.router.add_get("/api/proposal/{id}/reject", self.reject_api)

    async def index_handler(self, request):
        await self.memory.initialize()
        health = SystemTools.get_system_health()
        py_procs = SystemTools.find_active_python_processes()
        health["active_python_processes"] = len(py_procs)

        skills = await self.memory.list_skills(status="ACTIVE")
        benchmarks = await self.memory.get_latest_benchmarks(1)
        proposals = await self.memory.get_pending_proposals()

        latest_bench = benchmarks[0] if benchmarks else {
            "score": "N/A", "max_score": "100", "benchmark_name": "No benchmarks run yet"
        }

        # Simple fast template injection without heavy Jinja2 overhead
        html = (TEMPLATES_DIR / "dashboard.html").read_text(encoding="utf-8")
        html = html.replace("{{ status.autonomy_level }}", str(CURRENT_AUTONOMY_LEVEL))
        html = html.replace("{{ health.status }}", str(health["status"]))
        html = html.replace("{{ health.os }}", str(health["os"]))
        html = html.replace("{{ health.used_ram_pct }}", str(health["used_ram_pct"]))
        html = html.replace("{{ health.available_ram_gb }}", str(health["available_ram_gb"]))
        html = html.replace("{{ health.total_ram_gb }}", str(health["total_ram_gb"]))
        html = html.replace("{{ health.cpu_usage_pct }}", str(health["cpu_usage_pct"]))
        html = html.replace("{{ health.active_python_processes }}", str(health["active_python_processes"]))
        html = html.replace("{{ latest_benchmark.score }}", str(latest_bench["score"]))
        html = html.replace("{{ latest_benchmark.max_score }}", str(latest_bench["max_score"]))
        html = html.replace("{{ latest_benchmark.benchmark_name }}", str(latest_bench["benchmark_name"]))

        # Build skills rows
        skill_rows = ""
        for s in skills:
            skill_rows += (
                f"<tr><td style='font-weight:600;color:#38bdf8;'>{s['name']}</td>"
                f"<td>{s['purpose']}</td>"
                f"<td><span style='color:#10b981;'>{s['risk_level']}</span></td>"
                f"<td><span class='badge'>{s['status']}</span></td></tr>"
            )
        # Replace Jinja block with generated rows
        if "{% for skill in skills %}" in html:
            before = html.split("{% for skill in skills %}")[0]
            after = html.split("{% endfor %}")[1]
            html = before + skill_rows + after

        # Build proposal rows
        prop_rows = ""
        for p in proposals:
            prop_rows += (
                f"<tr><td>{p['title']}</td>"
                f"<td><a href='/api/proposal/{p['id']}/approve' class='btn'>Approve</a> "
                f"<a href='/api/proposal/{p['id']}/reject' class='btn btn-danger'>Reject</a></td></tr>"
            )
        if "{% for p in proposals %}" in html:
            p_split = html.split("{% if proposals %}")[1].split("{% else %}")
            part_body = p_split[0]
            after_else = p_split[1].split("{% endif %}")[1]
            
            if proposals:
                table_str = (
                    "<table><thead><tr><th>Title</th><th>Action</th></tr></thead><tbody>"
                    f"{prop_rows}</tbody></table>"
                )
                html = html.split("{% if proposals %}")[0] + table_str + after_else
            else:
                html = html.split("{% if proposals %}")[0] + (
                    "<p style='color:#94a3b8;font-size:13px;margin-top:10px;'>"
                    "No pending self-upgrades. DEVI is running on approved baseline.</p>"
                ) + after_else

        return web.Response(text=html, content_type="text/html")

    async def status_api(self, request):
        health = SystemTools.get_system_health()
        skills = await self.memory.list_skills()
        return web.json_response({
            "name": DEVI_NAME,
            "autonomy_level": CURRENT_AUTONOMY_LEVEL,
            "health": health,
            "skills_count": len(skills)
        })

    async def approve_api(self, request):
        pid = int(request.match_info["id"])
        await self.memory.decide_proposal(pid, "APPROVED")
        raise web.HTTPFound(location="/")

    async def reject_api(self, request):
        pid = int(request.match_info["id"])
        await self.memory.decide_proposal(pid, "REJECTED")
        raise web.HTTPFound(location="/")

    def run(self):
        print(f"[*] DEVI Evolution Dashboard starting on http://127.0.0.1:{self.port}")
        web.run_app(self.app, host="127.0.0.1", port=self.port)

if __name__ == "__main__":
    server = DashboardApp()
    server.run()
