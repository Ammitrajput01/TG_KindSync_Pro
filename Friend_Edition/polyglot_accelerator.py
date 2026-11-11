#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
TG KINDSYNC PRO — FRIEND EDITION POLYGLOT ACCELERATOR UNIFIED PROXY
=============================================================================
Seamlessly links to the canonical unified root polyglot_accelerator.py engine.
=============================================================================
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from polyglot_accelerator import *
