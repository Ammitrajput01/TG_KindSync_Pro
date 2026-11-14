# -*- coding: utf-8 -*-
"""
Devi Operator TMA 8.0 Cryptographic Authentication & Biometric Gatekeeper
Implements official Telegram WebApp HMAC-SHA256 initData validation.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

import hmac
import hashlib
import json
import urllib.parse
from typing import Optional, Dict, Any, Tuple

MASTER_ADMIN_IDS = (1553619403, 759038032)

def verify_tma_init_data(init_data_raw: str, bot_token: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Validates Telegram WebApp initData string using official Telegram Bot API specification:
    secret_key = HMAC_SHA256("WebAppData", bot_token)
    data_check_string = sorted_key_value_pairs_separated_by_newlines
    hash = HMAC_SHA256(secret_key, data_check_string)
    """
    if not init_data_raw or not bot_token:
        return False, None, "Missing initData or bot_token"

    try:
        parsed_data = urllib.parse.parse_qsl(init_data_raw, keep_blank_values=True)
        data_dict = dict(parsed_data)
        
        received_hash = data_dict.pop("hash", None)
        if not received_hash:
            return False, None, "Missing hash in initData"

        # Construct data_check_string from sorted pairs
        sorted_pairs = sorted(data_dict.items(), key=lambda x: x[0])
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_pairs)

        # Generate HMAC-SHA256 signature
        secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(computed_hash, received_hash):
            return False, None, "Invalid cryptographic HMAC signature"

        user_raw = data_dict.get("user")
        user_obj = json.loads(user_raw) if user_raw else {}
        
        return True, user_obj, "Valid TMA Session"

    except Exception as e:
        return False, None, f"TMA Auth Error: {str(e)}"

def is_master_admin(user_id: int) -> bool:
    """Verifies whether user_id belongs to the two hard-pinned Master Admins."""
    return user_id in MASTER_ADMIN_IDS
