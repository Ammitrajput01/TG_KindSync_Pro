#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-export of root fast_transfer for devi.operator package compatibility.
"""
import sys
from pathlib import Path

# Add project root to path if needed
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fast_transfer import (
    ParallelTransferrer,
    DownloadSender,
    UploadSender,
    fast_download,
    fast_upload,
)

__all__ = [
    "ParallelTransferrer",
    "DownloadSender",
    "UploadSender",
    "fast_download",
    "fast_upload",
]
