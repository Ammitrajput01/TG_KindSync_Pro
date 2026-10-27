"""
Universal Media Downloader & Auto-Topic Uploader Engine
======================================================
Powered by yt-dlp and FFmpeg for Telegram Supergroups, Forums, and Topics.
Supports:
- YouTube (Single Videos, Shorts, Community Posts, Full Playlists)
- Instagram (Reels, Posts, Carousels, IGTV)
- Twitter / X (Videos, GIFs)
- Direct Web Download Links (.mp4, .pdf, .mkv, .zip, etc.)
- Automatic Forum Topic targeting (message_thread_id)
- High-definition video thumbnails & ThumbEnforcer branding
- Clean clinical & educational metadata tags (#Lecture, #KindDoctor)
- Automatic post-upload temporary file purge to protect disk storage
"""

import os
import sys
import re
import asyncio
import logging
import shutil
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

try:
    import imageio_ffmpeg
    DEFAULT_FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    DEFAULT_FFMPEG_EXE = shutil.which("ffmpeg")

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

logger = logging.getLogger("DEVI.MediaDownloader")

BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
DOWNLOADS_DIR = BASE_PROJECT_DIR / "cache" / "media_downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)


def get_ffmpeg_binary() -> Optional[str]:
    """Resolves active FFmpeg binary path across Windows/Linux."""
    if DEFAULT_FFMPEG_EXE and os.path.isfile(DEFAULT_FFMPEG_EXE):
        return DEFAULT_FFMPEG_EXE
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    return None


def format_duration(seconds: Optional[int | float]) -> str:
    """Formats duration in seconds to HH:MM:SS or MM:SS."""
    if not seconds or seconds <= 0:
        return "N/A"
    sec = int(seconds)
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def format_bytes(size_bytes: Optional[int]) -> str:
    """Formats file size into human-readable MB / GB."""
    if not size_bytes or size_bytes <= 0:
        return "Unknown"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    if size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def is_supported_url(url: str) -> bool:
    """Quick validation for YouTube, Instagram, Twitter, or direct media URLs."""
    if not url:
        return False
    u = url.strip().lower()
    if re.search(r'(?:youtube\.com|youtu\.be|instagram\.com|twitter\.com|x\.com|tiktok\.com|facebook\.com|fb\.watch|vimeo\.com|reddit\.com)', u):
        return True
    if re.search(r'\.(mp4|mkv|mov|avi|flv|webm|mp3|m4a|pdf|zip|rar)(?:\?.*)?$', u):
        return True
    return False


def is_direct_file_url(url: str) -> bool:
    """Detects if URL is a direct downloadable HTTP file."""
    if not url:
        return False
    clean = url.strip().lower().split("?")[0]
    return bool(re.search(r'\.(mp4|mkv|mov|avi|webm|mp3|m4a|pdf|zip|rar)$', clean))


def sanitize_filename(name: str) -> str:
    """Sanitizes file name for OS filesystem safety."""
    cleaned = re.sub(r'[\\/*?:"<>|]', '_', name)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned[:120] if len(cleaned) > 120 else cleaned


class MediaDownloaderEngine:
    """Enterprise-grade, non-blocking media downloader with progress telemetry."""

    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or DOWNLOADS_DIR
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_exe = get_ffmpeg_binary()

    def _get_base_ydl_opts(self) -> Dict[str, Any]:
        opts: Dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "logtostderr": False,
            "outtmpl": str(self.download_dir / "%(title).100B-%(id)s.%(ext)s"),
            "writethumbnail": True,
        }
        if self.ffmpeg_exe:
            opts["ffmpeg_location"] = self.ffmpeg_exe
        return opts

    async def extract_info(self, url: str, max_playlist_items: int = 50) -> Dict[str, Any]:
        """Extracts media metadata without downloading the file."""
        if not YT_DLP_AVAILABLE:
            raise RuntimeError("yt-dlp is not installed in the python environment.")

        def _extract():
            opts = self._get_base_ydl_opts()
            opts["skip_download"] = True
            opts["playlistend"] = max_playlist_items
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await asyncio.to_thread(_extract)
        if not info:
            raise ValueError(f"Could not extract info for URL: {url}")

        is_playlist = "entries" in info and bool(info.get("entries"))
        title = info.get("title", "Unknown Media")
        uploader = info.get("uploader") or info.get("channel") or info.get("creator") or "Unknown Author"

        if is_playlist:
            raw_entries = [e for e in info.get("entries", []) if e]
            entries_summary = []
            total_duration = 0
            for idx, entry in enumerate(raw_entries, 1):
                dur = entry.get("duration", 0) or 0
                total_duration += dur
                entries_summary.append({
                    "index": idx,
                    "title": entry.get("title", f"Track {idx}"),
                    "id": entry.get("id"),
                    "url": entry.get("webpage_url") or entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "duration": dur,
                    "duration_str": format_duration(dur),
                    "thumbnail": entry.get("thumbnail"),
                })
            return {
                "is_playlist": True,
                "title": title,
                "uploader": uploader,
                "count": len(entries_summary),
                "total_duration_sec": total_duration,
                "total_duration_str": format_duration(total_duration),
                "entries": entries_summary,
                "url": url,
            }

        duration = info.get("duration", 0) or 0
        thumbnail = info.get("thumbnail")
        filesize_est = info.get("filesize") or info.get("filesize_approx") or 0
        width = info.get("width")
        height = info.get("height")
        resolution = f"{height}p" if height else "HD"

        return {
            "is_playlist": False,
            "title": title,
            "uploader": uploader,
            "duration_sec": duration,
            "duration_str": format_duration(duration),
            "filesize_est": filesize_est,
            "filesize_str": format_bytes(filesize_est),
            "thumbnail": thumbnail,
            "resolution": resolution,
            "width": width,
            "height": height,
            "description": info.get("description", "")[:400],
            "url": url,
        }

    async def download_single_media(
        self,
        url: str,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Downloads a single video/audio track with best compatibility (1080p/720p MP4).
        Returns metadata dict with local file paths.
        """
        if not YT_DLP_AVAILABLE:
            raise RuntimeError("yt-dlp is not installed.")

        def _download():
            opts = self._get_base_ydl_opts()
            # Choose best mp4 video under 2GB, or best video+audio merged to mp4
            opts["format"] = "bestvideo[ext=mp4][filesize<1900M]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            opts["merge_output_format"] = "mp4"
            opts["writethumbnail"] = True
            opts["noplaylist"] = True

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_filename = ydl.prepare_filename(info)
                # In case format merge created .mp4
                base_stem = Path(video_filename).stem
                final_video_path = None
                
                # Probe likely output paths
                candidates = [
                    Path(video_filename),
                    self.download_dir / f"{base_stem}.mp4",
                    self.download_dir / f"{base_stem}.mkv",
                    self.download_dir / f"{base_stem}.webm",
                ]
                for cand in candidates:
                    if cand.is_file() and cand.stat().st_size > 0:
                        final_video_path = cand
                        break

                # Probe thumbnail
                thumb_candidates = [
                    self.download_dir / f"{base_stem}.jpg",
                    self.download_dir / f"{base_stem}.webp",
                    self.download_dir / f"{base_stem}.png",
                    Path(f"{video_filename}.jpg"),
                ]
                final_thumb_path = None
                for tcand in thumb_candidates:
                    if tcand.is_file() and tcand.stat().st_size > 0:
                        final_thumb_path = tcand
                        break

                return info, final_video_path, final_thumb_path

        info, video_path, thumb_path = await asyncio.to_thread(_download)
        if not video_path or not video_path.is_file():
            raise FileNotFoundError(f"Failed to find downloaded video file for {url}")

        duration = info.get("duration", 0) or 0
        title = info.get("title", video_path.stem)
        uploader = info.get("uploader") or info.get("channel") or "Unknown Author"
        filesize = video_path.stat().st_size

        return {
            "title": title,
            "uploader": uploader,
            "duration_sec": duration,
            "duration_str": format_duration(duration),
            "filesize": filesize,
            "filesize_str": format_bytes(filesize),
            "file_path": str(video_path),
            "thumb_path": str(thumb_path) if thumb_path else None,
            "width": info.get("width"),
            "height": info.get("height"),
            "url": url,
        }

    async def download_direct_file(
        self,
        url: str,
        session: Optional[aiohttp.ClientSession] = None,
        progress_callback=None
    ) -> Dict[str, Any]:
        """Downloads direct HTTP/HTTPS media/document links with chunk streaming."""
        own_session = False
        if session is None:
            session = aiohttp.ClientSession()
            own_session = True

        try:
            parsed_name = url.split("?")[0].split("/")[-1] or "downloaded_file.bin"
            clean_name = sanitize_filename(parsed_name)
            target_path = self.download_dir / f"{int(asyncio.get_event_loop().time())}_{clean_name}"

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=600)) as resp:
                if resp.status != 200:
                    raise ValueError(f"HTTP {resp.status} while downloading direct link: {url}")
                total_bytes = int(resp.headers.get("content-length", 0))
                downloaded = 0
                with open(target_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(65536):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)

            filesize = target_path.stat().st_size
            return {
                "title": clean_name,
                "uploader": "Web Direct Stream",
                "duration_sec": 0,
                "duration_str": "N/A",
                "filesize": filesize,
                "filesize_str": format_bytes(filesize),
                "file_path": str(target_path),
                "thumb_path": None,
                "is_direct": True,
                "url": url,
            }
        finally:
            if own_session:
                await session.close()

    @staticmethod
    def cleanup_files(*paths: Optional[str | Path]):
        """Safely removes temporary download artifacts from disk."""
        for p in paths:
            if p:
                try:
                    f = Path(p)
                    if f.is_file():
                        f.unlink(missing_ok=True)
                except Exception as e:
                    logger.debug(f"File cleanup notice for {p}: {e}")

    @staticmethod
    def format_media_caption(
        title: str | Dict[str, Any],
        duration_str: Optional[str] = None,
        uploader: Optional[str] = None,
        index: Optional[int] = None,
        total: Optional[int] = None,
        custom_tags: Optional[str] = None
    ) -> str:
        """Constructs an elegant, high-yield clinical Telegram caption."""
        if isinstance(title, dict):
            info = title
            t_val = info.get("title", "Medical Lecture")
            d_val = info.get("duration_str") or format_duration(info.get("duration", 0) or 0)
            u_val = info.get("uploader") or info.get("channel") or "Kind Doctor Faculty"
            idx_val = index or info.get("index")
            tot_val = total or info.get("total")
        else:
            t_val = str(title)
            d_val = duration_str or "N/A"
            u_val = uploader or "Unknown Channel"
            idx_val = index
            tot_val = total

        brand_tags = "#MedicalLecture #KindDoctor"
        if custom_tags:
            tags = f"{brand_tags} {custom_tags}".strip()
        elif isinstance(title, dict) and title.get("tags"):
            tags = f"{brand_tags} {title.get('tags')}".strip()
        else:
            tags = f"{brand_tags} #ClinicalRevision"

        prefix = f"<b>Part {idx_val:02d}/{tot_val:02d}:</b> " if idx_val and tot_val else "🎬 "
        
        caption_lines = [
            f"{prefix}<b>{t_val}</b>",
            "",
            f"👤 <b>Faculty / Channel:</b> <code>{u_val}</code>",
            f"⏱️ <b>Duration:</b> <code>{d_val}</code> | ⚡ <b>HD Stream</b>",
            "",
            f"🏷️ <i>{tags}</i>",
            f"🩺 <i>Synced via Kind Doctor Bot Media Engine</i>"
        ]
        return "\n".join(caption_lines)


# Singleton Engine Instance
media_engine = MediaDownloaderEngine()
format_media_caption = MediaDownloaderEngine.format_media_caption
cleanup_files = MediaDownloaderEngine.cleanup_files
