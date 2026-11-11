---
name: telethon-async-concurrency
description: Master Telethon, MTProto, and async high-performance Telegram engineering. Covers FloodWait handling, upload/download bounded concurrency, session persistence, SQLite WAL, Cryptg acceleration, rate limiting, and graceful shutdown.
---

# Telethon & Async Telegram High-Performance Engineering

## 1. Core MTProto Architecture
- Use `TelegramClient(session_name, api_id, api_hash)` with explicit session path.
- Always install `cryptg` for C-accelerated encryption (up to 10x faster file transfers).
- Ensure SQLite session uses WAL mode (`PRAGMA journal_mode=WAL;`) to avoid database locking during concurrent reads/writes.

## 2. FloodWait & Rate-Limit Resilience
```python
import asyncio
from telethon.errors import FloodWaitError, FloodError

async def safe_execute(coro_fn, *args, max_retries=5, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            return await coro_fn(*args, **kwargs)
        except FloodWaitError as e:
            wait_time = e.seconds + 2
            # Log warning and sleep boundedly
            await asyncio.sleep(wait_time)
            retries += 1
        except FloodError:
            await asyncio.sleep(10)
            retries += 1
    raise RuntimeError("Max retries exceeded due to FloodWait.")
```

## 3. Bounded Concurrency & Backpressure
- NEVER spawn unbounded `asyncio.create_task` loops for downloading/uploading media.
- Use `asyncio.Semaphore(value=4)` to bound simultaneous file operations.
- Use `asyncio.Queue(maxsize=100)` with worker consumer loops for bounded memory consumption.

## 4. Chunked File Upload/Download Optimization
- Configure chunk sizes appropriately (typically 512KB chunks for large media).
- Track progress callbacks with debouncing to prevent event-loop choking.

## 5. Graceful Disconnect & Shutdown
```python
async def shutdown(client):
    if client.is_connected():
        await client.disconnect()
```
