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

def test_clean_cloned_caption_rich_formatting():
    """Verify Title formatting, filename fallback, and Kind Doctor signature."""
    # Case 1: Raw video text
    cap1 = clean_cloned_caption("61 Electron transport chain", is_media=True)
    assert "Title: 61 Electron transport chain" in cap1
    assert "📚 **Kind Doctor & Team**" in cap1
    assert "Group Study Help 😉" in cap1

    # Case 2: Empty text with filename
    cap2 = clean_cloned_caption("", orig_filename="1._How_to_study_OBG_using_Marrow_Edition_6.mp4", is_media=True)
    assert "Title: 1. How to study OBG using Marrow Edition 6" in cap2
    assert "📚 **Kind Doctor & Team**" in cap2

    # Case 3: Section banner preserved
    cap3 = clean_cloned_caption("✨ 🩺 OBSTETRICS & GYNAECOLOGY ✨")
    assert cap3 == "✨ 🩺 OBSTETRICS & GYNAECOLOGY ✨"

def test_clone_status_card_and_reset_flow():
    """Verify _build_clone_status_card_data renders interactive inline keyboards for both empty and active states."""
    from devi.operator.telegram_bot import DeviTelegramBot
    bot = DeviTelegramBot()

    # 1. Status with no jobs
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM telegram_clone_jobs WHERE user_id = 999888")
        conn.commit()

    text_empty, kb_empty = bot._build_clone_status_card_data(admin_id=999888)
    assert "No active clone jobs running currently" in text_empty
    assert any("act_cloner_reset" in btn["callback_data"] for row in kb_empty["inline_keyboard"] for btn in row)

    # 2. Status with active jobs
    job_id = create_clone_job(user_id=999888, source_chat="-1001", target_chat="-1002", job_type="group")
    text_active, kb_active = bot._build_clone_status_card_data(admin_id=999888)
    assert f"Job #{job_id}" in text_active
    assert any("act_cloner_stop_all" in btn["callback_data"] for row in kb_active["inline_keyboard"] for btn in row)

    # Clean up
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM telegram_clone_jobs WHERE user_id = 999888")
        conn.commit()

def test_title_repetition_sanitizer():
    """Verify that multiple stacked 'Title: Title: ...' prefixes are collapsed to a single clean Title."""
    raw = "Title: Title: Title: Anatomy Lecture 01 - Thorax Anatomy.mp4\n📚 **Kind Doctor & Team**\n💬 Group Study Help 😉"
    cleaned = clean_cloned_caption(raw)
    assert cleaned.startswith("Title: Anatomy Lecture 01 - Thorax Anatomy")
    assert cleaned.count("Title:") == 1

def test_user_isolation_status_card():
    """Verify strict tenant isolation between User A and User B in cloner status cards."""
    from devi.operator.telegram_bot import DeviTelegramBot
    bot = DeviTelegramBot()

    user_a = 111222333
    user_b = 444555666

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM telegram_clone_jobs WHERE user_id IN (?, ?)", (user_a, user_b))
        conn.commit()

    # User A starts a job
    job_a = create_clone_job(user_id=user_a, source_chat="-100111", target_chat="-100222", job_type="group")
    
    # User A checks status -> sees Job A
    text_a, _ = bot._build_clone_status_card_data(admin_id=user_a)
    assert f"Job #{job_a}" in text_a

    # User B checks status -> MUST NOT see Job A!
    text_b, _ = bot._build_clone_status_card_data(admin_id=user_b)
    assert f"Job #{job_a}" not in text_b
    assert "No active clone jobs running currently" in text_b

    # Clean up
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM telegram_clone_jobs WHERE user_id IN (?, ?)", (user_a, user_b))
        conn.commit()



