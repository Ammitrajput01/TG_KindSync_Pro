#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
TG KINDSYNC PRO V14.5 — COMPATIBILITY SHIM
================================================================================
This file is kept for backward compatibility with existing tests and scripts.
All core engine functionality has been upgraded and renamed to:
    tg_kindsync_pro.py
================================================================================
"""

import sys
from tg_kindsync_pro import *

# Export all symbols from tg_kindsync_pro into this module namespace
import tg_kindsync_pro
for attr in dir(tg_kindsync_pro):
    if not attr.startswith("__"):
        globals()[attr] = getattr(tg_kindsync_pro, attr)
