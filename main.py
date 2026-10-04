#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TG KindSync Pro 🩺 V15.0.0 – Main Entrypoint
Pure Deterministic High-Speed Streaming Engine
Created By: Dr. Amit Singh (Kind Doctor)
"""

import sys
import asyncio
from contextlib import suppress

if hasattr(sys.stdout, "reconfigure"):
    with suppress(Exception):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    with suppress(Exception):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import logging
logging.getLogger("telethon.crypto.libssl").setLevel(logging.ERROR)
logging.getLogger("telethon.crypto.aes").setLevel(logging.ERROR)

from tg_kindsync_pro import start_platform, release_lock

if __name__ == "__main__":
    try:
        asyncio.run(start_platform())
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        release_lock()
