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
    NATIVE_CRYPTO_ACTIVE
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
