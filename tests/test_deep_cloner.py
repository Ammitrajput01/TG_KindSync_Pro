#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for Deep Cloner Engine (200k+ messages, 2,000+ topics, watermark stripping).
"""

import sys
import sqlite3
import pytest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from devi.operator.deep_cloner import (
    clean_cloned_caption, create_clone_job,
    update_clone_job_progress, get_clone_job,
    get_active_clone_jobs, DB_PATH
)

def test_clean_cloned_caption_stripping():
    """Verify clean_cloned_caption removes handles, links, and promo watermarks."""
    dirty_text = (
        "0001_Biochemistry - Lecture 02 (SS 6 @AnandxBotss _wm)\n"
        "Uploaded by @RandomPirateBot Join for more lectures:\n"
        "https://t.me/joinchat/Abc12345XYZ\n\n"
        "Clinical Case: 45-year-old male with ketoacidosis."
    )
    cleaned = clean_cloned_caption(dirty_text)

    # Bot handle and links must be stripped
    assert "@AnandxBotss" not in cleaned
    assert "@RandomPirateBot" not in cleaned
    assert "t.me/joinchat" not in cleaned
    assert "_wm" not in cleaned

    # Clinical content must be preserved
    assert "Biochemistry - Lecture 02" in cleaned
    assert "Clinical Case: 45-year-old male with ketoacidosis." in cleaned

def test_clone_job_sqlite_lifecycle():
    """Verify clone job creation, progress updates, and retrieval."""
    user_id = 999001
    source_chat = "-1003912970546"
    target_chat = "-1001234567890"

    job_id = create_clone_job(user_id, source_chat, target_chat, job_type="group")
    assert job_id > 0

    job = get_clone_job(job_id)
    assert job is not None
    assert job["source_chat"] == source_chat
    assert job["status"] == "running"
    assert job["cloned_messages"] == 0

    # Update progress
    update_clone_job_progress(
        job_id,
        cloned_inc=25,
        last_msg_id=500,
        current_topic_title="Pharmacology",
        total_topics=150,
        completed_topics=10
    )

    updated_job = get_clone_job(job_id)
    assert updated_job["cloned_messages"] == 25
    assert updated_job["last_msg_id"] == 500
    assert updated_job["current_topic_title"] == "Pharmacology"
    assert updated_job["total_topics"] == 150
    assert updated_job["completed_topics"] == 10

    # Mark completed
    update_clone_job_progress(job_id, status="completed")
    completed_job = get_clone_job(job_id)
    assert completed_job["status"] == "completed"

    # Clean up test row
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM telegram_clone_jobs WHERE id = ?", (job_id,))
        conn.commit()
