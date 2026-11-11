#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TG KINDSYNC PRO — FRIEND EDITION UNIFIED COMPATIBILITY PROXY
=============================================================================
Seamlessly forwards execution to the canonical unified root tg_kindsync_pro.py.
Guarantees 100% single source of truth, zero maintenance drift, and full parity.
=============================================================================
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import all canonical modules, functions, and state from unified root
from tg_kindsync_pro import *

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
