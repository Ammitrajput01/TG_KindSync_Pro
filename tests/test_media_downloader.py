"""
Test Suite: Universal Media Downloader & In-Topic Uploader Engine
Tests url detection, caption formatting, ffmpeg discovery, cleanup, and bot command integration.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from devi.operator.media_downloader import (
    media_engine,
    is_supported_url,
    is_direct_file_url,
    format_media_caption,
    cleanup_files,
    MediaDownloaderEngine
)


def test_url_detection():
    print("[TEST] Testing URL Detection Logic...")
    
    # Supported URLs
    assert is_supported_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert is_supported_url("https://youtu.be/dQw4w9WgXcQ")
    assert is_supported_url("https://www.youtube.com/playlist?list=PL123456789")
    assert is_supported_url("https://www.instagram.com/reel/C123456789/")
    assert is_supported_url("https://twitter.com/user/status/123456789")
    assert is_supported_url("https://x.com/user/status/123456789")
    assert is_supported_url("https://www.tiktok.com/@user/video/123456789")
    
    # Unsupported or invalid URLs
    assert not is_supported_url("https://random-unsupported-site.org/page.html")
    assert not is_supported_url("not a url at all")
    assert not is_supported_url("ftp://example.com/file")
    print("  -> URL detection: PASSED")


def test_direct_file_url_detection():
    print("[TEST] Testing Direct File URL Detection...")
    assert is_direct_file_url("https://example.com/lectures/cardiology_lecture_01.mp4")
    assert is_direct_file_url("https://storage.googleapis.com/bucket/pathology_notes.pdf")
    assert is_direct_file_url("https://cdn.site.com/archive.zip")
    assert is_direct_file_url("https://videos.org/embryology.mkv")
    
    # Non-file URLs
    assert not is_direct_file_url("https://example.com/lectures/")
    assert not is_direct_file_url("https://example.com/watch?v=123")
    print("  -> Direct File URL detection: PASSED")


def test_caption_formatting():
    print("[TEST] Testing Media Caption Formatting...")
    info = {
        "title": "Dr. Najeeb - Action Potentials and ECG Waves",
        "uploader": "Dr. Najeeb Lectures",
        "duration": 3665,  # 1h 1m 5s
        "webpage_url": "https://youtube.com/watch?v=test1234"
    }
    
    caption = format_media_caption(info, custom_tags="#Cardiology #ECG")
    assert "Dr. Najeeb - Action Potentials and ECG Waves" in caption
    assert "Dr. Najeeb Lectures" in caption
    assert "1:01:05" in caption
    assert "#MedicalLecture" in caption
    assert "#KindDoctor" in caption
    assert "#Cardiology" in caption
    assert len(caption) <= 1024  # Telegram caption limit check
    print("  -> Caption Formatting: PASSED")


def test_ffmpeg_and_engine_init():
    print("[TEST] Testing FFmpeg Discovery & Engine Init...")
    engine = MediaDownloaderEngine()
    ffmpeg_path = engine.ffmpeg_exe
    assert ffmpeg_path is not None
    assert len(ffmpeg_path) > 0
    print(f"  -> Resolved FFmpeg Binary: {ffmpeg_path}")
    print("  -> Engine Init: PASSED")


def test_cleanup_utility():
    print("[TEST] Testing File Cleanup Utility...")
    temp_dir = tempfile.gettempdir()
    dummy_file = os.path.join(temp_dir, "test_kindsync_dummy.tmp")
    with open(dummy_file, "w") as f:
        f.write("temporary test data")
    
    assert os.path.exists(dummy_file)
    cleanup_files(dummy_file)
    assert not os.path.exists(dummy_file)
    print("  -> File Cleanup: PASSED")


def test_bot_command_definitions():
    print("[TEST] Testing Telegram Bot Command Integrations...")
    from devi.operator.telegram_bot import DeviTelegramBot
    
    bot = DeviTelegramBot()
    help_text, help_kb = bot._build_interactive_help_card(category="media")
    assert "/ytdl" in help_text
    assert "/upload" in help_text
    assert "/playlist" in help_text
    assert "/setgroup" in help_text
    assert "DEEP CLONER & UNIVERSAL MEDIA UPLOADER" in help_text or "UNIVERSAL MEDIA" in help_text
    print("  -> Bot Interactive Help Card: PASSED")


def test_multi_group_resolution():
    print("[TEST] Testing Multi-Group Topic & Chat Resolution...")
    from devi.operator.telegram_bot import DeviTelegramBot
    
    bot = DeviTelegramBot()
    # 1. In-group commands: strictly return the group itself
    assert bot._resolve_study_group_id(-1003912970546) == -1003912970546
    assert bot._resolve_study_group_id(-100999888) == -100999888
    
    # 2. Private DM with active preference set in memory
    bot.admin_active_group[1553619403] = -1003912970546
    assert bot._resolve_study_group_id(1553619403, admin_id=1553619403) == -1003912970546
    
    # Switch active preference to another group
    bot.admin_active_group[1553619403] = -100999888
    assert bot._resolve_study_group_id(1553619403, admin_id=1553619403) == -100999888
    
    # 3. Group Title Resolver
    title = bot._get_group_title(-1003912970546)
    assert title is not None
    assert len(title) > 0
    print(f"  -> Resolved group title for -1003912970546: {title}")
    print("  -> Multi-Group Resolution: PASSED")


def run_media_downloader_suite():
    print("\n========================================================")
    print("   UNIVERSAL IN-TOPIC MEDIA DOWNLOADER TEST SUITE")
    print("========================================================\n")
    test_url_detection()
    test_direct_file_url_detection()
    test_caption_formatting()
    test_ffmpeg_and_engine_init()
    test_cleanup_utility()
    test_bot_command_definitions()
    test_multi_group_resolution()
    print("\n[SUCCESS] ALL MEDIA DOWNLOADER TESTS PASSED 100%!\n")


if __name__ == "__main__":
    run_media_downloader_suite()
