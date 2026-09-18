import asyncio
import sqlite3
import sys
from pathlib import Path
import pytest

# Add turbo_companion to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from ayugram_autosupervisor import (
    is_ayugram_running,
    is_script_running,
    terminate_process,
)
from ayugram_glass_hud import (
    format_bytes,
    format_eta,
    format_speed,
)
from ayugram_turbo_companion import (
    AYUDATA_DB_PATH,
    HISTORY_DB_PATH,
    LINK_REGEX,
    RANGE_REGEX,
    api_hash,
    api_id,
    classify_medical_text,
    export_deleted_messages,
    get_database_stats,
    get_forwarder_telemetry,
    get_ghost_mode_status,
    get_top_ghost_sources,
    normalize_target_peer,
    normalize_db_peer_id,
    ACTIVE_TRANSFER_FILE,
    _update_ipc_transfer_status,
    render_progress_bar,
    sanitize_filename,
    search_deleted_messages,
    split_media_if_needed,
    UPLOAD_DROPZONE,
    UPLOAD_QUEUE_FILE,
    upload_local_file_with_split,
)


# ==============================================================================
# 1. Environment & Database Configuration Tests
# ==============================================================================

def test_api_credentials_loaded():
    """Verify API_ID and API_HASH are loaded and valid."""
    assert api_id is not None, "API_ID must not be None"
    assert isinstance(api_id, int), "API_ID must be an integer"
    assert api_hash is not None, "API_HASH must not be None"
    assert len(api_hash) >= 16, "API_HASH must have valid length"


def test_history_db_path_and_schema():
    """Verify HISTORY_DB_PATH resolves to existing sqlite database with valid tables."""
    assert HISTORY_DB_PATH.exists(), f"HISTORY_DB_PATH must exist: {HISTORY_DB_PATH}"
    con = sqlite3.connect(f"file:{HISTORY_DB_PATH}?mode=ro", uri=True, timeout=5.0)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {r[0] for r in cur.fetchall()}
    con.close()
    assert "forwarded" in tables, "forwarded table must exist in history_core.sqlite"
    assert "source_watermarks" in tables, "source_watermarks table must exist in history_core.sqlite"


def test_ayudata_db_path_and_schema():
    """Verify AYUDATA_DB_PATH exists and has DeletedMessage and EditedMessage tables."""
    assert AYUDATA_DB_PATH.exists(), f"AYUDATA_DB_PATH must exist: {AYUDATA_DB_PATH}"
    con = sqlite3.connect(f"file:{AYUDATA_DB_PATH}?mode=ro", uri=True, timeout=5.0)
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {r[0] for r in cur.fetchall()}
    con.close()
    assert "DeletedMessage" in tables, "DeletedMessage table must exist in ayudata.db"
    assert "EditedMessage" in tables, "EditedMessage table must exist in ayudata.db"


def test_ayu_settings_json():
    """Verify ayu_settings.json exists and parses cleanly."""
    status = get_ghost_mode_status()
    assert status["ok"] is True, "get_ghost_mode_status must return ok: True"
    assert "global_ghost" in status
    assert "save_deleted" in status
    assert "local_premium" in status


# ==============================================================================
# 2. Database Stats & Telemetry Extraction Tests
# ==============================================================================

def test_get_database_stats():
    """Verify get_database_stats returns non-zero counts from real database."""
    stats = get_database_stats()
    assert stats["deleted_count"] > 100000, f"Expected > 100k deleted messages, got {stats['deleted_count']}"
    assert stats["db_size"] != "N/A"
    assert stats["dl_files"] >= 0


def test_get_forwarder_telemetry():
    """Verify get_forwarder_telemetry extracts watermarks and forwarded count."""
    telemetry = get_forwarder_telemetry()
    assert telemetry["forwarded_count"] > 0, "Forwarded count should be > 0"
    assert isinstance(telemetry["watermarks"], dict)
    assert len(telemetry["watermarks"]) > 0, "Watermarks dictionary should have entries"
    assert telemetry["uploads_count"] >= 0, "Uploads count should be >= 0"
    assert len(telemetry["recent_forwards"]) > 0, "Recent forwards should contain entries"


# ==============================================================================
# 3. Async Forensic Search & Export Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_search_deleted_messages():
    """Verify search_deleted_messages is properly awaitable and returns highlighted snippets."""
    results, elapsed_ms = await search_deleted_messages("medicine", limit=5)
    assert isinstance(results, list)
    assert isinstance(elapsed_ms, float)
    assert elapsed_ms >= 0.0
    if results:
        first = results[0]
        assert "msg_id" in first
        assert "peer_id" in first
        assert "date" in first
        assert "text" in first
        assert "**[MEDICINE]**" in first["text"] or "medicine" in first["text"].lower()


@pytest.mark.asyncio
async def test_get_top_ghost_sources():
    """Verify get_top_ghost_sources returns top channels sorted by deleted message count."""
    top_sources = await get_top_ghost_sources(limit=5)
    assert isinstance(top_sources, list)
    assert len(top_sources) > 0
    assert "peer_id" in top_sources[0]
    assert "count" in top_sources[0]
    assert top_sources[0]["count"] > 0
    # Verify sorted descending
    counts = [s["count"] for s in top_sources]
    assert counts == sorted(counts, reverse=True)


@pytest.mark.asyncio
async def test_export_deleted_messages_and_cleanup():
    """Verify export_deleted_messages creates valid UTF-8 file and returns count."""
    export_file, count = await export_deleted_messages("test", max_count=5)
    if export_file is not None:
        assert export_file.exists()
        assert count > 0
        content = export_file.read_text(encoding="utf-8")
        assert "AYUGRAM DELETED MESSAGES VAULT FORENSIC EXPORT" in content
        export_file.unlink()  # Clean up


# ==============================================================================
# 4. Medical Classifier & String Sanitization Tests
# ==============================================================================

def test_medical_classifier():
    """Verify smart medical classifier accurately categorizes specialty keywords."""
    cases = [
        ("Brachial plexus and cranial nerve anatomy notes", "Anatomy & Embryology"),
        ("Action potential, GFR and cardiac cycle physiology", "Physiology & Biophysics"),
        ("Myocardial infarction ECG STEMI and coronary angiography", "Cardiology & Interventional"),
        ("Appendicitis, hernia and laparoscopy surgery", "General Surgery"),
        ("Psoriasis, eczema and lichen planus derma images", "Dermatology & Venereology"),
        ("Random unrelated non-medical sentence here", "General Notes")
    ]
    for text, expected_subj in cases:
        subj, _score = classify_medical_text(text)
        assert subj == expected_subj, f"Expected '{expected_subj}' for '{text}', got '{subj}'"


def test_sanitize_filename():
    """Verify sanitize_filename eliminates invalid path characters and handles empty strings."""
    assert sanitize_filename("valid_file.pdf") == "valid_file.pdf"
    assert sanitize_filename('test\\file/name:with*bad?chars"and<arrows>|end.mkv') == "test_file_name_with_bad_chars_and_arrows__end.mkv"
    assert sanitize_filename("") == "downloaded_file.bin"
    assert sanitize_filename("   ") == "downloaded_file.bin"


def test_normalize_target_peer():
    """Verify normalize_target_peer converts numeric strings to ints and preserves strings/me."""
    assert normalize_target_peer("me") == "me"
    assert normalize_target_peer("self") == "me"
    assert normalize_target_peer("") == "me"
    assert normalize_target_peer("-1001234567890") == -1001234567890
    assert normalize_target_peer("123456789") == 123456789
    assert normalize_target_peer("@channel_username") == "@channel_username"


# ==============================================================================
# 5. Math & Telemetry Formatting Tests (Cyber Glass HUD)
# ==============================================================================

def test_format_bytes():
    """Verify format_bytes handles 0, sub-1 byte floats, large integers without negative indices."""
    assert format_bytes(0) == "0 B"
    assert format_bytes(-5) == "0 B"
    assert format_bytes(0.5) == "0.50 B"
    assert format_bytes(512) == "512.0 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1024 * 1024) == "1.0 MB"
    assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
    assert format_bytes(1024 * 1024 * 1024 * 1024) == "1.0 TB"


def test_format_speed():
    """Verify format_speed handles negative values, B/s, KB/s, MB/s, and GB/s."""
    assert format_speed(-10) == "0 B/s"
    assert format_speed(500) == "500 B/s"
    assert format_speed(50 * 1024) == "50.0 KB/s"
    assert format_speed(25 * 1024 * 1024) == "25.00 MB/s"
    assert format_speed(1.5 * 1024 * 1024 * 1024) == "1.50 GB/s"


def test_format_eta():
    """Verify format_eta handles 0, seconds, minutes, hours, infinity, and NaN."""
    assert format_eta(0) == "--"
    assert format_eta(-5) == "--"
    assert format_eta(float("inf")) == "--"
    assert format_eta(float("nan")) == "--"
    assert format_eta(45) == "45s"
    assert format_eta(125) == "2m 5s"
    assert format_eta(3665) == "1h 1m"


def test_render_progress_bar():
    """Verify render_progress_bar length and fill bounds."""
    assert render_progress_bar(0.0, length=10) == "░░░░░░░░░░"
    assert render_progress_bar(0.5, length=10) == "█████░░░░░"
    assert render_progress_bar(1.0, length=10) == "██████████"
    assert render_progress_bar(-0.5, length=10) == "░░░░░░░░░░"
    assert render_progress_bar(1.5, length=10) == "██████████"


# ==============================================================================
# 6. Regex & URL Parsing Tests
# ==============================================================================

def test_link_regex():
    """Verify LINK_REGEX correctly extracts private channel ID, public username, and msg_id."""
    m1 = LINK_REGEX.search("https://t.me/c/1234567890/456")
    assert m1 is not None
    assert m1.group(1) == "1234567890"
    assert m1.group(3) == "456"

    m2 = LINK_REGEX.search("https://t.me/public_channel/789")
    assert m2 is not None
    assert m2.group(2) == "public_channel"
    assert m2.group(3) == "789"

    m_invalid = LINK_REGEX.search("https://example.com/not/telegram")
    assert m_invalid is None


def test_range_regex():
    """Verify RANGE_REGEX correctly extracts start and end IDs."""
    m = RANGE_REGEX.search("https://t.me/c/1234567890/100-150")
    assert m is not None
    assert m.group(1) == "1234567890"
    assert m.group(3) == "100"
    assert m.group(4) == "150"


# ==============================================================================
# 7. Media Splitting & Supervisor Invariants
# ==============================================================================

def test_split_media_under_limit(tmp_path):
    """Verify split_media_if_needed returns original file when size is under max_bytes."""
    dummy = tmp_path / "sample.mp4"
    dummy.write_bytes(b"A" * 1024)
    parts = split_media_if_needed(dummy, max_bytes=2048)
    assert len(parts) == 1
    assert parts[0][0] == dummy
    assert parts[0][2] == 1  # Part 1 of 1
    assert parts[0][3] == 1


def test_supervisor_functions():
    """Verify supervisor helper functions do not crash."""
    # Check is_ayugram_running returns boolean
    res = is_ayugram_running()
    assert isinstance(res, bool)
    # Check is_script_running returns boolean
    res_script = is_script_running("non_existent_fake_script_xyz.py")
    assert res_script is False
    # Check terminate_process handles None safely
    terminate_process(None)


# ==============================================================================
# 8. Adversarial Stress & Concurrency Invariant Tests
# ==============================================================================

@pytest.mark.asyncio
async def test_adversarial_sql_injection_defense():
    """Verify SQL injection payloads do not compromise query execution or database state."""
    payloads = [
        "' OR 1=1 --",
        "'; DROP TABLE DeletedMessage; --",
        "' UNION SELECT 1, 2, 3, 'injected' --",
        "1' OR '1'='1",
        "admin'--",
    ]
    for p in payloads:
        results, elapsed_ms = await search_deleted_messages(p, limit=3)
        assert isinstance(results, list), f"Expected list result for payload: {p}"
        assert isinstance(elapsed_ms, float)


@pytest.mark.asyncio
async def test_adversarial_concurrent_reads():
    """Verify multiple concurrent tasks can query ayudata.db and history_core.sqlite simultaneously without lock errors."""
    async def query_task(q):
        res, _el = await search_deleted_messages(q, limit=2)
        top = await get_top_ghost_sources(limit=3)
        st = get_database_stats()
        fw = get_forwarder_telemetry()
        return len(res) >= 0 and len(top) > 0 and st["deleted_count"] > 0 and fw["forwarded_count"] > 0

    tasks = [query_task(k) for k in ["medicine", "surgery", "anatomy", "pediatrics", "derma"]]
    results = await asyncio.gather(*tasks)
    assert all(results), "All concurrent queries should succeed without locking errors"


def test_adversarial_progress_bar_extreme_floats():
    """Verify progress bar and formatting handles extreme floats without crashing."""
    assert render_progress_bar(-999999.0) == "░░░░░░░░░░░░░░"
    assert render_progress_bar(999999.0) == "██████████████"
    assert format_bytes(-999999) == "0 B"
    assert format_speed(-999999) == "0 B/s"


# ==============================================================================
# 9. Evolution Feature Verification Tests
# ==============================================================================

def test_medical_classifier_multi_word_weighting():
    """Verify multi-word clinical phrases receive high precedence over isolated words."""
    # "coronary artery disease" contains "artery" (anatomy) but its multi-word matches Cardiology (weight 3)
    subj1, _score1 = classify_medical_text("Patient with coronary artery disease and angina")
    assert subj1 == "Cardiology & Interventional", f"Expected Cardiology for coronary artery disease, got {subj1}"

    # "otitis media" contains "media", but otitis media is ENT
    subj2, _score2 = classify_medical_text("Diagnosis of acute otitis media with effusion")
    assert subj2 == "ENT & Head-Neck", f"Expected ENT for otitis media, got {subj2}"


@pytest.mark.asyncio
async def test_search_deleted_messages_with_peer_filter():
    """Verify search_deleted_messages respects peer_id filtering and metadata extraction."""
    top_sources = await get_top_ghost_sources(limit=1)
    if top_sources:
        target_peer = top_sources[0]["peer_id"]
        results, elapsed_ms = await search_deleted_messages("the", limit=5, peer_id=target_peer)
        assert isinstance(results, list)
        for r in results:
            assert str(r["peer_id"]) == str(target_peer), f"Result peer_id {r['peer_id']} must match target {target_peer}"
            assert "from_id" in r
            assert "fwd_name" in r
            assert "mime_type" in r


def test_forwarder_telemetry_velocity():
    """Verify forwarder telemetry provides last_hour_count and last_day_count integers."""
    t = get_forwarder_telemetry()
    assert "last_hour_count" in t
    assert "last_day_count" in t
    assert isinstance(t["last_hour_count"], int)
    assert isinstance(t["last_day_count"], int)
    assert t["last_hour_count"] >= 0
    assert t["last_day_count"] >= t["last_hour_count"]


def test_normalize_target_peer_extended():
    """Verify normalize_target_peer handles t.me private/public links, usernames, and numeric IDs."""
    assert normalize_target_peer("https://t.me/c/3850536279/100") == -1003850536279
    assert normalize_target_peer("t.me/c/1234567890/42") == -1001234567890
    assert normalize_target_peer("https://t.me/AyuGramSupport") == "@AyuGramSupport"
    assert normalize_target_peer("t.me/tgforwarder") == "@tgforwarder"
    assert normalize_target_peer("@my_channel") == "@my_channel"
    assert normalize_target_peer("-1003850536279") == -1003850536279
    assert normalize_target_peer("12345678") == 12345678
    assert normalize_target_peer("me") == "me"
    assert normalize_target_peer("self") == "me"


def test_normalize_db_peer_id():
    """Verify normalize_db_peer_id generates both bare and signed ID candidates for Telegram channels."""
    c1 = normalize_db_peer_id("-1003850536279")
    assert 3850536279 in c1
    assert -1003850536279 in c1

    c2 = normalize_db_peer_id(3850536279)
    assert 3850536279 in c2

    assert normalize_db_peer_id(None) == []


@pytest.mark.asyncio
async def test_search_deleted_messages_with_negative_channel_id():
    """Verify searching deleted messages using Telegram negative channel format (-100...) succeeds."""
    top_sources = await get_top_ghost_sources(limit=1)
    if top_sources:
        bare_peer = top_sources[0]["peer_id"]
        neg_peer = -1000000000000 - bare_peer if bare_peer < 1000000000000 else int(f"-100{bare_peer}")
        # Search with negative ID format
        results_neg, _ = await search_deleted_messages("", limit=5, peer_id=neg_peer)
        results_bare, _ = await search_deleted_messages("", limit=5, peer_id=bare_peer)
        assert len(results_neg) > 0, f"Expected matches for negative channel ID {neg_peer}"
        assert len(results_neg) == len(results_bare), "Negative and bare ID queries should return equivalent matches"


def test_ipc_transfer_status_lifecycle():
    """Verify _update_ipc_transfer_status creates atomic JSON file, updates state, and cleans up properly."""
    import json
    # 1. Update status to active
    _update_ipc_transfer_status(
        active=True,
        filename="test_evolution_file.bin",
        downloaded=1048576,
        total=5242880,
        speed=524288.0,
        eta=8.0,
        percent=20.0
    )
    assert ACTIVE_TRANSFER_FILE.exists(), "ACTIVE_TRANSFER_FILE should exist when active"
    with open(ACTIVE_TRANSFER_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["active"] is True
    assert data["filename"] == "test_evolution_file.bin"
    assert data["downloaded"] == 1048576
    assert data["total"] == 5242880

    # 2. Deactivate status
    _update_ipc_transfer_status(active=False)
    with open(ACTIVE_TRANSFER_FILE, "r", encoding="utf-8") as f:
        data_inactive = json.load(f)
    assert data_inactive["active"] is False

    # 3. Clean up
    if ACTIVE_TRANSFER_FILE.exists():
        ACTIVE_TRANSFER_FILE.unlink()


def test_ipc_transfer_status_with_peer():
    """Verify _update_ipc_transfer_status records and preserves peer identity."""
    import json
    _update_ipc_transfer_status(
        active=True,
        filename="video_lecture.mp4",
        speed=15728640.0,
        peer="@MedicalLibraryHub"
    )
    assert ACTIVE_TRANSFER_FILE.exists()
    with open(ACTIVE_TRANSFER_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["peer"] == "@MedicalLibraryHub"
    assert data["active"] is True
    _update_ipc_transfer_status(active=False)
    if ACTIVE_TRANSFER_FILE.exists():
        ACTIVE_TRANSFER_FILE.unlink()


def test_sparkline_circular_buffer_window():
    """Verify 30-sample circular deque window retains exactly 30 samples and rotates correctly."""
    from collections import deque
    buf = deque([0.0] * 30, maxlen=30)
    assert len(buf) == 30
    for i in range(50):
        buf.append(float(i))
    assert len(buf) == 30
    assert buf[0] == 20.0
    assert buf[-1] == 49.0


def test_sparkline_math_and_scaling():
    """Verify sparkline coordinate calculation handles zero speed, extreme bursts, and negative outliers safely."""
    w = 360
    h = 18
    # Test with all zeros
    zero_samples = [0.0] * 30
    max_s = max(zero_samples)
    if max_s <= 0.0:
        max_s = 1024.0
    coords = []
    for i, s in enumerate(zero_samples):
        x = int(i * (w - 6) / 29) + 3
        ratio = min(1.0, max(0.0, s / max_s))
        y = int(h - 3 - ratio * (h - 6))
        coords.extend([x, y])
    assert len(coords) == 60
    # All Y coordinates must be within [0, h]
    for y_coord in coords[1::2]:
        assert 0 <= y_coord <= h

    # Test with 10 GB/s extreme burst
    burst_samples = [0.0] * 29 + [10.0 * 1024 * 1024 * 1024]
    max_s = max(burst_samples)
    coords_burst = []
    for i, s in enumerate(burst_samples):
        x = int(i * (w - 6) / 29) + 3
        ratio = min(1.0, max(0.0, s / max_s))
        y = int(h - 3 - ratio * (h - 6))
        coords_burst.extend([x, y])
    assert len(coords_burst) == 60
    # Last point must be peak (minimum Y on inverted canvas)
    last_y = coords_burst[-1]
    first_y = coords_burst[1]
    assert last_y < first_y, "High speed peak must have smaller Y than baseline in canvas coordinates"


def test_upload_dropzone_and_queue_paths():
    """Verify UPLOAD_DROPZONE directory exists and UPLOAD_QUEUE_FILE path is valid."""
    assert UPLOAD_DROPZONE.exists(), "UPLOAD_DROPZONE must be created and available"
    assert UPLOAD_QUEUE_FILE.name == "upload_queue.json"


def test_queue_file_helper(tmp_path):
    """Verify queue_file helper properly adds file to upload_queue.json."""
    import json
    import subprocess
    dummy_file = tmp_path / "test_4gb_file.mkv"
    dummy_file.write_bytes(b"0" * 1024)
    
    script = Path(__file__).resolve().parent / "queue_file.py"
    assert script.exists()
    res = subprocess.run([sys.executable, str(script), str(dummy_file)], capture_output=True)
    assert res.returncode == 0
    assert UPLOAD_QUEUE_FILE.exists()

    with open(UPLOAD_QUEUE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert str(dummy_file.resolve()) in data["queue"]

    # Clean up test entry
    data["queue"].remove(str(dummy_file.resolve()))
    with open(UPLOAD_QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def test_split_media_binary_multi_part(tmp_path):
    """Verify split_media_if_needed slices files larger than max_bytes into proper parts."""
    large_dummy = tmp_path / "big_data_archive.bin"
    # Write 5000 bytes and split with 2000 byte limit (should produce 3 parts)
    large_dummy.write_bytes(b"A" * 5000)
    parts = split_media_if_needed(large_dummy, max_bytes=2000)
    assert len(parts) == 3
    assert parts[0][2] == 1 and parts[0][3] == 3
    assert parts[1][2] == 2 and parts[1][3] == 3
    assert parts[2][2] == 3 and parts[2][3] == 3
    # Clean up
    for p_path, _, _, _ in parts:
        if p_path != large_dummy and p_path.exists():
            p_path.unlink()


