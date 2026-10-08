import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from devi.operator.telegram_bot import DeviTelegramBot, API_ID, API_HASH

def test_api_id_and_hash_defined():
    assert API_ID is not None
    assert isinstance(API_ID, int)
    assert API_ID > 0
    assert API_HASH is not None
    assert len(API_HASH) > 0

def test_autoforward_panel_structure():
    bot = DeviTelegramBot(bot_token="123456:TEST_TOKEN_FAKE")
    text, markup = bot._build_autoforward_panel_data(user_id=1553619403)
    
    assert "AUTO FORWARD" in text.upper() or "ACCOUNT" in text.upper()
    assert "inline_keyboard" in markup
    
    # Check that core buttons exist in layout
    cb_data_list = [btn["callback_data"] for row in markup["inline_keyboard"] for btn in row if "callback_data" in btn]
    assert "act_fwd_vip" in cb_data_list
    assert "act_fwd_login" in cb_data_list
    assert "act_fwd_add_src" in cb_data_list
    assert "act_fwd_add_tgt" in cb_data_list
    assert "act_fwd_del_src" in cb_data_list
    assert "act_fwd_del_tgt" in cb_data_list
    assert "act_fwd_settings" in cb_data_list
    assert "act_fwd_start" in cb_data_list
