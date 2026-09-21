#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for DEVI Unbounded Autonomous Self-Evolution Expansion Suite (Part 5).
"""

import pytest
import asyncio
from pathlib import Path

from devi.evolution.evolution_daemon import EvolutionDaemon
from devi.evolution.vitality_daemon import VitalityDaemon
from devi.evolution.self_healer import SelfHealer
from devi.evolution.evaluator import Evaluator
from devi.memory.memory_store import MemoryStore
from devi.config import DATABASE_PATH


@pytest.mark.asyncio
async def test_self_healer_multi_layer_scan():
    """Verify SelfHealer executes multi-layer diagnostic without errors."""
    memory = MemoryStore(DATABASE_PATH)
    await memory.initialize()
    healer = SelfHealer(memory)
    res = await healer.scan_and_heal()
    assert res["status"] in ("HEALTHY", "HEALED")
    assert isinstance(res["issues_resolved"], int)
    assert isinstance(res["actions"], list)


@pytest.mark.asyncio
async def test_evaluator_foundation_benchmark():
    """Verify Evaluator runs 6-part benchmark with score > 80."""
    memory = MemoryStore(DATABASE_PATH)
    await memory.initialize()
    evaluator = Evaluator(memory)
    res = await evaluator.run_foundation_benchmark()
    assert res["score"] >= 80.0
    assert res["max_score"] == 100.0
    assert "memory_integrity" in res["breakdown"]
    assert "sandbox_execution" in res["breakdown"]
    assert "sandbox_boundary_control" in res["breakdown"]
    assert "medical_calculator_validation" in res["breakdown"]
    assert "osint_and_rose_heuristics" in res["breakdown"]
    assert "evolution_record" in res["breakdown"]


@pytest.mark.asyncio
async def test_vitality_daemon_pulse_and_learning():
    """Verify VitalityDaemon scans keys, checks providers, and synthesizes universal learning."""
    daemon = VitalityDaemon.get_instance()
    await daemon.run_vitality_cycle()
    summary = daemon.get_summary()
    assert summary["name"] == "Devi Ji"
    assert summary["is_alive"] is True
    assert summary["active_providers_count"] >= 1
    assert "Devi Ji" in summary["latest_learning"]


@pytest.mark.asyncio
async def test_evolution_daemon_single_cycle():
    """Verify EvolutionDaemon runs full single cycle seamlessly."""
    daemon = EvolutionDaemon(interval_seconds=3600)
    cycle_res = await daemon.run_single_cycle()
    assert cycle_res["cycle_status"] == "SUCCESS"
    assert cycle_res["benchmark_score"] >= 80.0
    assert cycle_res["elapsed_ms"] > 0
