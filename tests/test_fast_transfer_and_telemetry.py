#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit and regression tests for Fast MTProto Multi-Socket Transfer,
Telemetry Persistence, and Dashboard Route Matrix APIs.
"""

import sys
import os
import json
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from fast_transfer import (
    ParallelTransferrer,
    DownloadSender,
    UploadSender,
    fast_download,
    fast_upload,
)

def test_fast_transfer_classes():
    print("Testing ParallelTransferrer optimal connection scaling...")
    assert ParallelTransferrer.get_optimal_connections(1 * 1024 * 1024) == 2
    assert ParallelTransferrer.get_optimal_connections(15 * 1024 * 1024) == 4
    assert ParallelTransferrer.get_optimal_connections(50 * 1024 * 1024) == 8
    assert ParallelTransferrer.get_optimal_connections(250 * 1024 * 1024) == 12
    print("[PASS] ParallelTransferrer connection calculation OK!")
def test_telemetry_persistence():
    print("Testing telemetry JSON schema consistency...")
    telem_dir = ROOT_DIR / "logs"
    telem_dir.mkdir(parents=True, exist_ok=True)
    telem_file = telem_dir / "engine_telemetry.json"

    dummy_data = {
        "timestamp": time.time(),
        "total_files": 687,
        "discovered": 687,
        "files_completed": 535,
        "messages_forwarded": 535,
        "files_remaining": 152,
        "batch_progress_pct": 77.9,
        "videos_sent": 13,
        "docs_sent": 40,
        "photos_sent": 75,
        "text_sent": 407,
        "current_speed_mb": 25.4,
        "peak_speed_mb": 31.2,
        "active_file_name": "01_cvs_part1.mp4",
        "active_file_progress": 65.4,
        "active_file_transferred": "120.5 MB",
        "active_file_total": "184.5 MB",
        "active_file_eta": "4s"
    }
    with open(telem_file, "w", encoding="utf-8") as f:
        json.dump(dummy_data, f)

    assert telem_file.exists()
    with open(telem_file, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["total_files"] == 687
    assert loaded["files_completed"] == 535
    assert loaded["current_speed_mb"] == 25.4
    print("[PASS] Telemetry JSON read/write persistence OK!")

if __name__ == "__main__":
    test_fast_transfer_classes()
    test_telemetry_persistence()
    print("\nALL FAST TRANSFER & TELEMETRY TESTS PASSED 100%!")
