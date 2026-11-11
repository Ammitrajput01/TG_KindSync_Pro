#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import socket
import pytest
from polyglot_accelerator import (
    fast_dumps,
    fast_loads,
    DuckDBVectorScanner,
    tune_socket_kernel_pacing,
    get_acceleration_status,
    HAS_ORJSON,
    HAS_DUCKDB,
    NATIVE_CRYPTO_ACTIVE,
    PredictiveFloodPacer,
    ConfigHotReloader,
    classify_medical_subject
)

def test_fast_json_roundtrip():
    data = {"system": "TG_KindSync_Pro", "version": 15, "polyglot": True, "active": [1, 2, 3]}
    serialized = fast_dumps(data)
    assert isinstance(serialized, str)
    deserialized = fast_loads(serialized)
    assert deserialized == data

def test_duckdb_vector_scanner_singleton():
    scanner = DuckDBVectorScanner.get_instance()
    assert scanner is not None
    assert scanner is DuckDBVectorScanner.get_instance()

def test_duckdb_vector_scan_ids_fallback():
    scanner = DuckDBVectorScanner.get_instance()
    # Test with non-existent or temporary path - should gracefully return empty set without crashing
    res = scanner.check_duplicate_ids("non_existent_history.sqlite", 123456, [1, 2, 3])
    assert isinstance(res, set)
    assert len(res) == 0

def test_tune_socket_kernel_pacing():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tune_socket_kernel_pacing(s)
        # TCP_NODELAY should be 1
        nodelay = s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)
        assert nodelay != 0
    finally:
        s.close()

def test_get_acceleration_status():
    status = get_acceleration_status()
    assert "crypto_engine" in status
    assert "json_engine" in status
    assert "analytics_engine" in status
    assert "event_loop" in status
    assert "platform" in status
    assert isinstance(status["has_orjson"], bool)
    assert isinstance(status["has_duckdb"], bool)

def test_classify_medical_subject():
    assert classify_medical_subject("056) Tumors of Kidney & Ureter.mp4") == "SURGERY"
    assert classify_medical_subject("004_Pharmacokinetics_Metabolism.mp4") == "PHARMACOLOGY"
    assert classify_medical_subject("Cranial Nerves Gross Anatomy.pdf") == "ANATOMY"
    assert classify_medical_subject("Unknown Random File.mp4") is None

def test_config_hot_reloader(tmp_path):
    test_env = tmp_path / "test.env"
    test_env.write_text("MESSAGE_DELAY=0.5\n", encoding="utf-8")
    assert ConfigHotReloader.check_and_reload(str(test_env)) is False # Initial load sets baseline
    
    # Wait small delta and update
    import time
    time.sleep(0.05)
    test_env.write_text("MESSAGE_DELAY=0.0\n", encoding="utf-8")
    ConfigHotReloader._last_check = 0.0 # Reset check debounce
    assert ConfigHotReloader.check_and_reload(str(test_env)) is True

def test_predictive_flood_pacer():
    import asyncio
    PredictiveFloodPacer._history = []
    async def _test():
        wait_time = await PredictiveFloodPacer.pace()
        assert wait_time == 0.0
        assert len(PredictiveFloodPacer._history) == 1

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(asyncio.run, _test()).result()
    else:
        asyncio.run(_test())

