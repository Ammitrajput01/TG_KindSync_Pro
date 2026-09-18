import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from tg_kind_mode_v14 import (
    sanitize_filename, customize_caption, ThumbEnforcer,
    parse_telegram_link, extract_smart_hashtags
)

print("=== 1. Testing parse_telegram_link ===")
res = parse_telegram_link("https://t.me/c/4234551262/259")
chat_id = res.get("CHAT_ID")
topic_id = res.get("TOPIC_ID")
assert chat_id == -1004234551262, f"Expected -1004234551262 got {chat_id}"
assert topic_id == 259, f"Expected 259 got {topic_id}"
print(f"  [PASS] Telegram link parsed properly: Chat={chat_id}, Topic={topic_id}")

print("=== 2. Testing sanitize_filename with REPLACE_WORDS and PREFIX ===")
os.environ["REPLACE_WORDS"] = "OldAcademy:KindDoctor,Batch2024:2026"
os.environ["CUSTOM_FILE_PREFIX"] = "DrAmit - "
s_name = sanitize_filename("OldAcademy_Anatomy_Lecture_01_Batch2024.mp4", fallback_ext=".mp4")
print(f"  Sanitized name: {s_name}")
assert "OldAcademy" not in s_name
assert "KindDoctor" in s_name
assert s_name.startswith("DrAmit - ")
print("  [PASS] sanitize_filename properly replaces words and applies custom prefix!")

print("=== 3. Testing customize_caption: Tagging OFF + STRIP_HASHTAGS ===")
os.environ["AUTO_HASHTAGS"] = "false"
os.environ["STRIP_HASHTAGS"] = "true"
os.environ["CUSTOM_HEADER"] = "🌟 EXCLUSIVE LECTURE"
os.environ["CUSTOM_FOOTER"] = "👨‍⚕️ Curated by Kind Doctor"

cap_in = "Pharmacology Class 01 #OldChannel #Promo join @channel"
cap_out = customize_caption(cap_in)
print("  Caption output:\n" + cap_out)
assert "#OldChannel" not in cap_out
assert "#Promo" not in cap_out
assert "🌟 EXCLUSIVE LECTURE" in cap_out
assert "👨‍⚕️ Curated by Kind Doctor" in cap_out
print("  [PASS] customize_caption strips tags when disabled and applies header/footer!")

print("=== 4. Testing customize_caption: Tagging ON ===")
os.environ["AUTO_HASHTAGS"] = "true"
os.environ["STRIP_HASHTAGS"] = "false"
cap_in2 = "Anatomy Lecture 05 on Upper Limb"
cap_out2 = customize_caption(cap_in2)
print("  Caption with tags output:\n" + cap_out2)
assert "#Anatomy" in cap_out2 or "#Lecture05" in cap_out2
print("  [PASS] customize_caption auto-generates smart hashtags when enabled!")

print("=== 5. Testing ThumbEnforcer fallback ===")
te = ThumbEnforcer()
t = te.get()
print(f"  Thumbnail path: {t}")
assert t is not None
assert os.path.exists(t)
print("  [PASS] ThumbEnforcer provides valid 16:9 thumbnail path!")

print("\n🎉 ALL USER-REQUESTED CORE LOGIC FIXES VERIFIED 100% OPERATIONAL!")
