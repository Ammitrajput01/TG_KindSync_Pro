#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for PipelineProcessor Media Streaming & Direct Forwarding Execution Flow.
Ensures that when direct_forward is False (Fast RAM Streaming Mode),
media files (videos, photos, docs) and text messages are properly processed and not skipped as errors.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from tg_kindsync_pro import PipelineProcessor, WorkItem, AppConfig, PerformanceConfig


class DummyMedia:
    def __init__(self):
        self.document = MagicMock()
        self.document.attributes = []


class DummyMessage:
    def __init__(self, msg_id, text="", is_video=False, is_text=False):
        self.id = msg_id
        self.text = text
        self.media = DummyMedia() if is_video else None
        self.video = MagicMock() if is_video else None
        self.document = None
        self.photo = None
        if is_video:
            f_mock = MagicMock()
            f_mock.name = "video_test.mp4"
            f_mock.size = 10485760
            self.file = f_mock
        else:
            self.file = None


@pytest.mark.asyncio
async def test_streaming_mode_executes_media_when_direct_forward_is_false():
    """Verify that when direct_forward is False, Tier 1 fast server-side copy is attempted and message is sent."""
    rpc = MagicMock()
    rpc.execute = AsyncMock(return_value=MagicMock(id=999, media=MagicMock()))

    streamer = MagicMock()
    streamer.stream_media = AsyncMock(return_value=MagicMock(name="video_test.mp4"))

    state = MagicMock()
    state.is_processed = AsyncMock(return_value=False)
    state.mark_completed = AsyncMock()

    cfg = AppConfig(
        api_id=12345,
        api_hash="test",
        source_chat=-100111,
        target_chat=-100222,
        direct_forward=False,
        routing_mode=1,
        perf=PerformanceConfig()
    )

    metrics = {
        "discovered": 10,
        "messages_forwarded": 0,
        "albums_forwarded": 0,
        "errors_count": 0,
        "videos_sent": 0,
        "docs_sent": 0,
        "photos_sent": 0,
        "text_sent": 0,
        "bytes_uploaded": 0,
    }

    dlq = MagicMock()
    dlq.append = AsyncMock()

    session_mgr = MagicMock()
    session_mgr.get_client = MagicMock(return_value=MagicMock())

    proc = PipelineProcessor(
        rpc=rpc,
        streamer=streamer,
        state=state,
        cfg=cfg,
        ui_log=MagicMock(),
        metrics=metrics,
        dlq=dlq,
        session_mgr=session_mgr
    )
    # Stub get_topic_title & headers
    proc.get_topic_title = AsyncMock(return_value="Test Topic")
    proc.resolve_topic_id = AsyncMock(return_value=None)
    proc.send_session_headers = AsyncMock()
    proc.check_and_send_subject_header = AsyncMock()

    video_msg = DummyMessage(msg_id=101, text="Sample Lecture Video", is_video=True)
    item = WorkItem(messages=[video_msg], rule_index=0)
    stop_event = asyncio.Event()

    await proc.execute(item, stop_event)

    # RPC send_file must be executed
    assert rpc.execute.called, "RPC execute must be called to send file"
    # Success metrics must be updated
    assert metrics["messages_forwarded"] == 1
    assert metrics["videos_sent"] == 1
    assert metrics["errors_count"] == 0
    # State manager must mark item completed
    assert state.mark_completed.called


@pytest.mark.asyncio
async def test_streaming_fallback_when_restricted():
    """Verify that when server-side copy is restricted, it seamlessly falls back to RAM streamer."""
    from telethon.errors import ChatForwardsRestrictedError

    rpc = MagicMock()
    # First call (direct send_file) raises ChatForwardsRestrictedError, second call (streamed send_file) succeeds
    rpc.execute = AsyncMock(side_effect=[
        ChatForwardsRestrictedError(request=MagicMock()),
        MagicMock(id=999, media=MagicMock())
    ])

    streamer = MagicMock()
    streamer.stream_media = AsyncMock(return_value=MagicMock(name="video_test.mp4"))

    state = MagicMock()
    state.is_processed = AsyncMock(return_value=False)
    state.mark_completed = AsyncMock()

    cfg = AppConfig(
        api_id=12345,
        api_hash="test",
        source_chat=-100111,
        target_chat=-100222,
        direct_forward=False,
        routing_mode=1,
        perf=PerformanceConfig()
    )

    metrics = {
        "discovered": 10,
        "messages_forwarded": 0,
        "albums_forwarded": 0,
        "errors_count": 0,
        "videos_sent": 0,
        "docs_sent": 0,
        "photos_sent": 0,
        "text_sent": 0,
        "bytes_uploaded": 0,
    }

    dlq = MagicMock()
    session_mgr = MagicMock()
    session_mgr.get_client = MagicMock(return_value=MagicMock())

    proc = PipelineProcessor(
        rpc=rpc,
        streamer=streamer,
        state=state,
        cfg=cfg,
        ui_log=MagicMock(),
        metrics=metrics,
        dlq=dlq,
        session_mgr=session_mgr
    )
    proc.get_topic_title = AsyncMock(return_value="Test Topic")
    proc.resolve_topic_id = AsyncMock(return_value=None)
    proc.send_session_headers = AsyncMock()
    proc.check_and_send_subject_header = AsyncMock()

    video_msg = DummyMessage(msg_id=101, text="Sample Lecture Video", is_video=True)
    item = WorkItem(messages=[video_msg], rule_index=0)
    stop_event = asyncio.Event()

    await proc.execute(item, stop_event)

    # Streamer MUST be called upon fallback
    assert streamer.stream_media.called, "Streamer must be called when server-side copy is restricted"
    assert metrics["messages_forwarded"] == 1
    assert metrics["videos_sent"] == 1
    assert state.mark_completed.called


@pytest.mark.asyncio
async def test_text_messages_marked_success_and_sent():
    """Verify that pure text messages are sent and not incremented as errors."""
    rpc = MagicMock()
    rpc.execute = AsyncMock(return_value=MagicMock(id=888))

    streamer = MagicMock()
    state = MagicMock()
    state.is_processed = AsyncMock(return_value=False)
    state.mark_completed = AsyncMock()

    cfg = AppConfig(
        api_id=12345,
        api_hash="test",
        source_chat=-100111,
        target_chat=-100222,
        direct_forward=False,
        routing_mode=1,
        perf=PerformanceConfig()
    )

    metrics = {
        "discovered": 10,
        "messages_forwarded": 0,
        "albums_forwarded": 0,
        "errors_count": 0,
        "videos_sent": 0,
        "docs_sent": 0,
        "photos_sent": 0,
        "text_sent": 0,
        "bytes_uploaded": 0,
    }

    dlq = MagicMock()
    dlq.append = AsyncMock()
    session_mgr = MagicMock()
    session_mgr.get_client = MagicMock(return_value=MagicMock())

    proc = PipelineProcessor(
        rpc=rpc,
        streamer=streamer,
        state=state,
        cfg=cfg,
        ui_log=MagicMock(),
        metrics=metrics,
        dlq=dlq,
        session_mgr=session_mgr
    )
    proc.get_topic_title = AsyncMock(return_value="Test Topic")
    proc.resolve_topic_id = AsyncMock(return_value=None)
    proc.send_session_headers = AsyncMock()
    proc.check_and_send_subject_header = AsyncMock()

    text_msg = DummyMessage(msg_id=102, text="Notes on Anatomy Chapter 1", is_video=False, is_text=True)
    item = WorkItem(messages=[text_msg], rule_index=0)
    stop_event = asyncio.Event()

    await proc.execute(item, stop_event)

    assert rpc.execute.called
    assert metrics["messages_forwarded"] == 1
    assert metrics["text_sent"] == 1
    assert metrics["errors_count"] == 0
    assert state.mark_completed.called

