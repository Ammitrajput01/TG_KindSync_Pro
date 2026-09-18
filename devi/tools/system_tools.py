"""
DEVI Operator Tool: System Diagnostics & Resource Monitor
Monitors CPU, RAM (16GB bounds), Disk space, and Python process health.
"""

import psutil
import os
import platform
from typing import Dict, Any

class SystemTools:
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        """
        Gathers memory, CPU, disk, and operating environment metrics.
        """
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        cpu_pct = psutil.cpu_percent(interval=0.1)

        total_ram_gb = vm.total / (1024 ** 3)
        available_ram_gb = vm.available / (1024 ** 3)
        used_ram_pct = vm.percent

        # Health status determination
        status = "HEALTHY"
        if used_ram_pct > 85 or cpu_pct > 90:
            status = "WARNING_HIGH_LOAD"
        elif used_ram_pct > 95:
            status = "CRITICAL_LOW_MEMORY"

        return {
            "status": status,
            "os": f"{platform.system()} {platform.release()}",
            "cpu_usage_pct": cpu_pct,
            "total_ram_gb": round(total_ram_gb, 2),
            "available_ram_gb": round(available_ram_gb, 2),
            "used_ram_pct": used_ram_pct,
            "free_disk_gb": round(disk.free / (1024 ** 3), 2),
            "total_disk_gb": round(disk.total / (1024 ** 3), 2)
        }

    @staticmethod
    def find_active_python_processes() -> list:
        """
        Discovers running python processes on the machine.
        """
        py_procs = []
        for p in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                name = p.info['name'] or ''
                if 'python' in name.lower():
                    mem_mb = (p.info['memory_info'].rss / (1024 * 1024)) if p.info['memory_info'] else 0
                    py_procs.append({
                        "pid": p.info['pid'],
                        "name": name,
                        "memory_mb": round(mem_mb, 1)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return py_procs
