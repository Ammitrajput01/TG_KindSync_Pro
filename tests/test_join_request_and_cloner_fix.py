import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import dis
import tg_kindsync_pro
import Friend_Edition.tg_kindsync_pro as friend_tg
from devi.operator.telegram_bot import DeviTelegramBot

def test_no_unbound_local_set_key_in_cloner():
    """Verify that 'set_key' is not treated as an uninitialized local variable in run_group_cloner_tool."""
    for mod in [tg_kindsync_pro, friend_tg]:
        func = getattr(mod, "run_group_cloner_tool", None)
        assert func is not None
        code = func.__code__
        # In Python bytecode, co_varnames contains all local variables.
        # 'set_key' MUST NOT be in co_varnames, it should be in co_names (global).
        assert "set_key" not in code.co_varnames, f"set_key found in local variables of {mod.__name__}.run_group_cloner_tool! This causes UnboundLocalError!"
        assert "set_key" in code.co_names, f"set_key should be resolved globally in {mod.__name__}.run_group_cloner_tool"

def test_handle_chat_join_request_dispatch():
    """Verify that _handle_chat_join_request builds OSINT radar and dispatches 1-click approve/decline buttons."""
    async def _runner():
        daemon = DeviTelegramBot(bot_token="123456:FAKE_TOKEN_FOR_TEST")
        daemon._send_message = AsyncMock(return_value=101)

        join_req = {
            "chat": {"id": -10099887766, "title": "Test Medical Group"},
            "from": {
                "id": 998877,
                "is_bot": False,
                "first_name": "Test",
                "last_name": "Applicant",
                "username": "testapplicant"
            },
            "bio": "Medical student preparing for NEET PG",
            "date": 1700000000
        }

        mock_session = MagicMock()
        await daemon._handle_chat_join_request(mock_session, join_req)

        # Master admins should receive the join request alert
        assert daemon._send_message.call_count >= len(daemon.master_admin_ids)
        msg_text = daemon._send_message.call_args_list[0][0][2]
        markup = daemon._send_message.call_args_list[0][1]["reply_markup"]

        assert "PENDING JOIN REQUEST" in msg_text
        assert "998877" in msg_text
        assert "Test Medical Group" in msg_text

        # Verify 1-click action buttons exist
        buttons = [btn["callback_data"] for row in markup["inline_keyboard"] for btn in row]
        assert "act_appr_join_-10099887766_998877" in buttons
        assert "act_decl_join_-10099887766_998877" in buttons
        assert "osint_user_998877" in buttons
        assert "ban_-10099887766_998877" in buttons

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(asyncio.run, _runner()).result()
    else:
        asyncio.run(_runner())

def run_test_suite():
    test_no_unbound_local_set_key_in_cloner()
    test_handle_chat_join_request_dispatch()
    print("[SUCCESS] ALL JOIN REQUEST & CLONER PROXY TESTS PASSED 100%!")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
