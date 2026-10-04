#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification suite for:
1. Filename Extension Preservation & MIME Type Inference
2. Word Stripping Whitespace Cleanup (no space before .mp4 / extensions)
3. Sleek Title & Caption Presentation (clean Title line without technical .mp4 junk)
"""

import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from tg_kindsync_pro import (
    apply_clean_rules,
    sanitize_filename,
    clean_index_title,
    customize_caption,
)

def test_apply_clean_rules():
    print("[*] 1. Testing apply_clean_rules for whitespace and extension handling...")
    
    # Test 1: yw stripping before .mp4
    t1 = apply_clean_rules("64. Tracheostomy and Foreign body in airway yw.mp4")
    assert " .mp4" not in t1, f"Found space before .mp4: '{t1}'"
    assert "yw" not in t1.lower(), f"'yw' was not stripped: '{t1}'"
    assert t1 == "64. Tracheostomy and Foreign body in airway.mp4", f"Unexpected result: '{t1}'"

    # Test 2: existing space before .mp4
    t2 = apply_clean_rules("64. Tracheostomy and Foreign body in airway .mp4")
    assert t2 == "64. Tracheostomy and Foreign body in airway.mp4", f"Unexpected result: '{t2}'"

    # Test 3: yw at end of text without extension
    t3 = apply_clean_rules("1.How to approach yw")
    assert t3.strip() == "1.How to approach", f"Unexpected result: '{t3}'"

    # Test 4: yw at end of long anatomy lecture title
    t4 = apply_clean_rules("2.Aoe - Layers , structure of eyeball and anatomy of cornea yw")
    assert t4.strip() == "2.Aoe - Layers, structure of eyeball and anatomy of cornea", f"Unexpected result: '{t4}'"

    print("  [+] apply_clean_rules whitespace & extension tests: 100% PASS")

def test_sanitize_filename():
    print("[*] 2. Testing sanitize_filename for extension preservation & MIME inference...")

    # Case 1: Video with yw before extension
    fn1 = sanitize_filename("64. Tracheostomy and Foreign body in airway yw.mp4")
    assert fn1 == "64. Tracheostomy and Foreign body in airway.mp4", f"Got '{fn1}'"

    # Case 2: Video without extension but fallback_ext='.mp4'
    fn2 = sanitize_filename("1.How to approach yw", fallback_ext=".mp4")
    assert fn2 == "1.How to approach.mp4", f"Got '{fn2}'"

    # Case 3: Video without extension but mime_type='video/mp4'
    fn3 = sanitize_filename("1.How to approach yw", mime_type="video/mp4")
    assert fn3 == "1.How to approach.mp4", f"Got '{fn3}'"

    # Case 4: Long anatomy lecture with mime_type='video/mp4'
    fn4 = sanitize_filename("2.Aoe - Layers , structure of eyeball and anatomy of cornea yw", mime_type="video/mp4")
    assert fn4 == "2.Aoe - Layers, structure of eyeball and anatomy of cornea.mp4", f"Got '{fn4}'"

    # Case 5: MKV video
    fn5 = sanitize_filename("Lecture 03 Biochem yw", mime_type="video/x-matroska")
    assert fn5 == "Lecture 03 Biochem.mkv", f"Got '{fn5}'"

    # Case 6: PDF document
    fn6 = sanitize_filename("Anatomy Notes Chapter 1 yw", mime_type="application/pdf")
    assert fn6 == "Anatomy Notes Chapter 1.pdf", f"Got '{fn6}'"

    print("  [+] sanitize_filename extension & MIME inference: 100% PASS")

def test_customize_caption():
    print("[*] 3. Testing customize_caption clean title formatting...")

    cap1 = customize_caption("64. Tracheostomy and Foreign body in airway yw.mp4")
    assert " .mp4" not in cap1, f"Found space before .mp4 in caption: '{cap1}'"
    assert "yw" not in cap1.lower(), f"'yw' not stripped from caption: '{cap1}'"
    assert "**Title**: 64. Tracheostomy and Foreign body in airway" in cap1, f"Title formatted incorrectly: '{cap1}'"

    cap2 = customize_caption("1.How to approach yw")
    assert "**Title**: 1.How to approach" in cap2, f"Title formatted incorrectly: '{cap2}'"

    cap3 = customize_caption("Title: 64. Tracheostomy and Foreign body in airway .mp4")
    assert " .mp4" not in cap3, f"Found space before .mp4 in caption: '{cap3}'"
    assert "Title: 64. Tracheostomy and Foreign body in airway" in cap3, f"Title formatted incorrectly: '{cap3}'"

    print("  [+] customize_caption clean title formatting: 100% PASS")

def test_clean_index_title():
    print("[*] 4. Testing clean_index_title...")

    t1 = clean_index_title("64. Tracheostomy and Foreign body in airway .mp4")
    assert " .mp4" not in t1 and ".mp4" not in t1, f"Got '{t1}'"
    assert t1 == "Tracheostomy and Foreign body in airway", f"Got '{t1}'"

    t2 = clean_index_title("1.How to approach yw")
    assert t2 == "How to approach", f"Got '{t2}'"

    print("  [+] clean_index_title: 100% PASS")

if __name__ == "__main__":
    print("=" * 60)
    print("   FILENAME EXTENSION & CAPTION FORMATTING AUDIT")
    print("=" * 60)
    test_apply_clean_rules()
    test_sanitize_filename()
    test_customize_caption()
    test_clean_index_title()
    print("=" * 60)
    print("   ALL EXTENSION & CAPTION TESTS PASSED 100%!")
    print("=" * 60)
