#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for Anti-DMCA Brand Obfuscation (Leet-Speak Matrix) Pipeline.
Ensures zero copyright keyword detection for bot crawlers across captions,
titles, filenames, and Telegram forum topic titles.
"""

import pytest
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from devi.operator.deep_cloner import (
    apply_anti_dmca_obfuscation,
    clean_cloned_caption,
    ANTI_DMCA_BRAND_MATRIX
)
from tg_kindsync_pro import apply_clean_rules, clean_index_title, sanitize_filename
from telethon.tl.types import DocumentAttributeFilename


def test_core_anti_dmca_brand_matrix():
    """Verify primary 4 targets mandated by Dr. Amit."""
    cases = [
        ("PrepLadder Surgery Lecture 01", "Prep L@dder Surgery Lecture 01"),
        ("DAMS Comprehensive Review", "D@MS Comprehensive Review"),
        ("Marrow Edition 6.5 Medicine", "M@rr0w Edition 6.5 Medicine"),
        ("Cerebellum Academy Grand Test", "Cer@bellum Academy Grand Test"),
    ]
    for raw, expected in cases:
        assert apply_anti_dmca_obfuscation(raw) == expected


def test_case_insensitivity_and_separators():
    """Verify obfuscation handles lowercase, uppercase, underscores, dots, and hyphens."""
    assert apply_anti_dmca_obfuscation("prepladder_surgery.mp4") == "Prep L@dder_surgery.mp4"
    assert apply_anti_dmca_obfuscation("PREPLADDER-NOTES") == "Prep L@dder-NOTES"
    assert apply_anti_dmca_obfuscation("dams_micro.pdf") == "D@MS_micro.pdf"
    assert apply_anti_dmca_obfuscation("marrow.edition.6") == "M@rr0w.edition.6"
    assert apply_anti_dmca_obfuscation("cerebellum_anat") == "Cer@bellum_anat"


def test_secondary_medical_platforms():
    """Verify secondary medical platforms are also obfuscated."""
    samples = [
        ("Bhatia TND", "Bh@ti@ TND"),
        ("DBMCI Quick Revision", "D.B.M.C.I Quick Revision"),
        ("First Aid USMLE Step 1", "1st A!d USMLE Step 1"),
        ("Pathoma Fundamentals", "P@thoma Fundamentals"),
        ("Sketchy Medical Microbiology", "Sk3tchy Medical Microbiology"),
        ("Ninja Nerd Cardiology", "N!nja N3rd Cardiology"),
        ("Dr. Najeeb Neuroanatomy", "Dr N@jeeb Neuroanatomy"),
        ("EGurukul Surgery", "E-Guruk@l Surgery"),
    ]
    for raw, expected in samples:
        assert apply_anti_dmca_obfuscation(raw) == expected


def test_no_unintended_corruption():
    """Verify common words containing substrings are never corrupted."""
    safe_words = [
        "fundamental",
        "macadam",
        "tomorrow",
        "dam",
        "ladder",
        "narrow",
        "arrow"
    ]
    for w in safe_words:
        assert apply_anti_dmca_obfuscation(w) == w


def test_clean_cloned_caption_full_pipeline():
    """Verify clean_cloned_caption protects titles, bodies, and handles third-party stripping."""
    raw = (
        "🎬 Title: Marrow Medicine Rapid Revision\n"
        "Join @BadChannel for DAMS and PrepLadder lectures\n"
        "https://t.me/fake_link\n"
        "Cerebellum notes attached below."
    )
    res = clean_cloned_caption(raw, is_media=True)
    assert "@BadChannel" not in res
    assert "fake_link" not in res
    assert "M@rr0w" in res
    assert "D@MS" in res
    assert "Prep L@dder" in res
    assert "Cer@bellum" in res
    assert "Kind Doctor & Team" in res


def test_document_attribute_filename_obfuscation():
    """Verify Telethon DocumentAttributeFilename can be updated in-place."""
    attr = DocumentAttributeFilename(file_name="PrepLadder_Pediatrics_Lec01.mp4")
    attr.file_name = apply_anti_dmca_obfuscation(attr.file_name)
    assert attr.file_name == "Prep L@dder_Pediatrics_Lec01.mp4"


def test_tg_kindsync_pro_integration():
    """Verify tg_kindsync_pro cleaning functions inherit anti-DMCA protection."""
    clean_txt = apply_clean_rules("Watch Marrow and DAMS on PrepLadder")
    assert "M@rr0w" in clean_txt
    assert "D@MS" in clean_txt
    assert "Prep L@dder" in clean_txt

    clean_t = clean_index_title("Marrow Obstetrics & Gynaecology")
    assert "M@rr0w" in clean_t

    clean_fn = sanitize_filename("Cerebellum_Anatomy_Session.pdf")
    assert "Cer@bellum" in clean_fn

