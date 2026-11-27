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
import glob
import html
import time
import importlib
import subprocess
import asyncio
import logging
import shutil
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

os.environ.setdefault("YTDLP_NO_PLUGINS", "1")

try:
    import imageio_ffmpeg
    DEFAULT_FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    DEFAULT_FFMPEG_EXE = shutil.which("ffmpeg")

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    yt_dlp = None
    YT_DLP_AVAILABLE = False

logger = logging.getLogger("DEVI.MediaDownloader")


def _isolate_yt_dlp_plugins() -> None:
    """Prevents stale external plugins (e.g. yt-dlp-youtube-oauth2) from hijacking YoutubeIE."""
    if not YT_DLP_AVAILABLE or yt_dlp is None:
        return
    try:
        import yt_dlp.globals as _yg
        _yg.plugin_dirs.value = []
        import yt_dlp.extractor.youtube._video as _yv
        cls = getattr(_yv, "YoutubeIE", None)
        while cls is not None and hasattr(cls, "__wrapped__") and (
            getattr(cls, "PLUGIN_NAME", None) or "oauth" in getattr(cls, "IE_NAME", "").lower()
        ):
            base = cls.__wrapped__
            sys.modules[base.__module__].YoutubeIE = base
            if hasattr(_yg, "plugin_ies_overrides") and base in _yg.plugin_ies_overrides.value:
                _yg.plugin_ies_overrides.value.pop(base, None)
            cls = base
    except Exception:
        pass


_isolate_yt_dlp_plugins()


class _YdlCaptureLogger:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def debug(self, msg):
        pass

    def warning(self, msg):
        if msg:
            self.warnings.append(str(msg))

    def error(self, msg):
        if msg:
            self.errors.append(str(msg))


_YTDLP_UPDATE_LOCK = asyncio.Lock()


async def maybe_update_yt_dlp(force: bool = False) -> bool:
    """Rate-limited (24h) auto-updater for yt-dlp to handle YouTube signature changes."""
    marker = Path(__file__).resolve().parent.parent.parent / "cache" / "ytdlp_update.ts"
    marker.parent.mkdir(parents=True, exist_ok=True)
    if not force and marker.exists():
        try:
            if time.time() - float(marker.read_text().strip() or 0) < 86400:
                return False
        except Exception:
            pass
    async with _YTDLP_UPDATE_LOCK:
        def _do_upd():
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "--no-deps", "-q", "yt-dlp"],
                capture_output=True, text=True, timeout=120,
            )
        try:
            await asyncio.to_thread(_do_upd)
            marker.write_text(str(time.time()))
            if yt_dlp is not None:
                importlib.reload(yt_dlp)
                _isolate_yt_dlp_plugins()
            return True
        except Exception:
            return False


def ensure_yt_dlp() -> bool:
    """Self-healing helper: automatically installs yt-dlp if missing from environment."""
    global yt_dlp, YT_DLP_AVAILABLE
    if YT_DLP_AVAILABLE and yt_dlp is not None:
        return True
    try:
        import yt_dlp as imported_ydl
        yt_dlp = imported_ydl
        YT_DLP_AVAILABLE = True
        return True
    except ImportError:
        pass

    logger.info("[!] yt-dlp not found in active python environment. Attempting self-healing pip install...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], timeout=180)
        import yt_dlp as imported_ydl
        yt_dlp = imported_ydl
        YT_DLP_AVAILABLE = True
        logger.info("[+] yt-dlp installed and imported successfully via self-healing pipeline!")
        return True
    except Exception as e:
        logger.error(f"[!] Self-healing pip install of yt-dlp failed: {e}")
        return False

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
    """Quick validation for YouTube, Instagram, TikTok, Snapchat, Twitter/X, and direct media URLs."""
    if not url:
        return False
    u = url.strip().lower()
    if re.search(r'(?:youtube\.com|youtu\.be|instagram\.com|twitter\.com|x\.com|tiktok\.com|snapchat\.com|facebook\.com|fb\.watch|vimeo\.com|reddit\.com|pinterest\.com|pin\.it|threads\.net|soundcloud\.com|spotify\.com|dailymotion\.com|bilibili\.com)', u):
        return True
    if re.search(r'\.(mp4|mkv|mov|avi|flv|webm|mp3|m4a|pdf|zip|rar)(?:\?.*)?$', u):
        return True
    return False


def is_hls_url(url: str) -> bool:
    u = url.lower().strip()
    return bool(re.search(r'\.(m3u8|mpd)(?:\?.*)?$', u)) or "format=m3u8" in u


def resolve_upload_thumbnail(downloaded_thumb: Optional[Path] = None) -> Optional[Path]:
    """Resolves 16:9 Kind Doctor cover when THUMB_MODE=custom, else converts downloaded thumb to JPG."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    thumb_mode = os.getenv("THUMB_MODE", "custom").strip().lower()
    enable_sig = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")
    if thumb_mode == "custom" and enable_sig:
        for cand in (root_dir / "tg_thumb_cached.jpg", root_dir / "kind_doctor_thumb.jpg", root_dir / "assets" / "thumb.jpg"):
            if cand.is_file() and cand.stat().st_size > 0:
                return cand
    if downloaded_thumb and downloaded_thumb.is_file() and downloaded_thumb.stat().st_size > 0:
        if downloaded_thumb.suffix.lower() in (".jpg", ".jpeg"):
            return downloaded_thumb
        try:
            from PIL import Image
            out_jpg = downloaded_thumb.with_suffix(".jpg")
            with Image.open(downloaded_thumb) as im:
                im.convert("RGB").save(out_jpg, "JPEG", quality=90)
            return out_jpg
        except Exception:
            return downloaded_thumb
    for cand in (root_dir / "tg_thumb_cached.jpg", root_dir / "kind_doctor_thumb.jpg"):
        if cand.is_file() and cand.stat().st_size > 0:
            return cand
    return None


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

        # Automatic Cookie Resolution for Datacenter / VPS Anti-Bot Bypass
        cookie_candidates = [
            BASE_PROJECT_DIR / "cookies.txt",
            Path("/home/ubuntu/TG_KindSync_Pro/cookies.txt"),
            Path("c:/TG_KindSync_Pro/cookies.txt"),
            Path("cookies.txt"),
        ]
        for c in cookie_candidates:
            if c.is_file() and c.stat().st_size > 0:
                opts["cookiefile"] = str(c)
                break

        # Anti-Bot JS Challenge Execution (Deno / Node.js)
        opts["remote_components"] = ["ejs:github"]
        deno_bin = shutil.which("deno") or (Path("/home/ubuntu/.deno/bin/deno") if Path("/home/ubuntu/.deno/bin/deno").is_file() else None)
        if deno_bin:
            opts["js_runtimes"] = {"deno": {"path": str(deno_bin)}}

        return opts

    async def extract_info(self, url: str, max_playlist_items: int = 50) -> Dict[str, Any]:
        """Extracts media metadata with oauth2 isolation and ordered player_client fallbacks."""
        if not YT_DLP_AVAILABLE and not ensure_yt_dlp():
            raise RuntimeError("yt-dlp is not installed in the python environment.")
        _isolate_yt_dlp_plugins()
        await maybe_update_yt_dlp(force=False)

        def _extract():
            base_opts = self._get_base_ydl_opts()
            has_cookies = bool(base_opts.get("cookiefile"))
            strategies = []
            if has_cookies:
                strategies.extend([
                    {"clients": ["web_embedded", "tv_samsung", "web"], "use_cookies": True},
                    {"clients": ["web_safari", "mweb", "tv"], "use_cookies": True},
                ])
            strategies.extend([
                {"clients": ["tv_samsung", "web_safari"], "use_cookies": False},
                {"clients": ["android_vr", "ios", "visionos"], "use_cookies": False},
            ])
            last_errors: List[str] = []
            for strat in strategies:
                cap_log = _YdlCaptureLogger()
                opts = dict(base_opts)
                opts["ignoreerrors"] = False
                opts["skip_download"] = True
                opts["extract_flat"] = "in_playlist"
                opts["playlistend"] = max_playlist_items
                opts["playlist_items"] = f"1:{max_playlist_items}"
                opts["logger"] = cap_log
                if not strat["use_cookies"]:
                    opts.pop("cookiefile", None)
                opts["extractor_args"] = {"youtube": {"player_client": strat["clients"]}}
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        res = ydl.extract_info(url, download=False)
                        if res:
                            return res, cap_log.errors
                except Exception as ex:
                    last_errors.append(f"{strat['clients']}: {str(ex)[:140]}")
                last_errors.extend(cap_log.errors[:2])
            raise RuntimeError("yt-dlp extraction failed: " + (" | ".join(last_errors[-3:]) or "No info returned"))

        info, _ = await asyncio.to_thread(_extract)
        if not info:
            raise ValueError(f"Could not extract info for URL: {url}")

        is_playlist = "entries" in info and bool(info.get("entries"))
        title = info.get("title", "Unknown Media")
        uploader = info.get("uploader") or info.get("channel") or info.get("creator") or "Unknown Author"

        if is_playlist:
            raw_entries = [e for e in info.get("entries", []) if e]
            raw_entries.sort(key=lambda e: int(e.get("playlist_index") or 999999))
            entries_summary = []
            total_duration = 0
            for idx, entry in enumerate(raw_entries, 1):
                dur = entry.get("duration", 0) or 0
                total_duration += dur
                entries_summary.append({
                    "index": int(entry.get("playlist_index") or idx),
                    "title": entry.get("title", f"Track {idx}"),
                    "id": entry.get("id"),
                    "url": entry.get("webpage_url") or entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "duration": dur,
                    "duration_str": format_duration(dur),
                    "thumbnail": entry.get("thumbnail"),
                })
            if not entries_summary:
                raise RuntimeError("Playlist yielded 0 accessible videos (check cookies.txt or playlist privacy).")
            entries_summary.sort(key=lambda x: x["index"])
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
        quality: Optional[str] = "best",
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Downloads a single video/audio track with requested quality (1080p, 720p, 480p, 360p, or MP3).
        Returns metadata dict with local file paths.
        """
        if not YT_DLP_AVAILABLE and not ensure_yt_dlp():
            raise RuntimeError("yt-dlp is not installed in the python environment.")

        def _download():
            opts = self._get_base_ydl_opts()
            opts["writethumbnail"] = True
            opts["noplaylist"] = True

            q = (quality or "best").strip().lower()
            if q in ("audio", "mp3", "m4a", "music"):
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            elif q in ("1080p", "1080", "fhd"):
                opts["format"] = "bestvideo[height<=1080][vcodec^=avc1]+bestaudio[acodec^=mp4a]/bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]/best"
                opts["merge_output_format"] = "mp4"
            elif q in ("720p", "720", "hd"):
                opts["format"] = "bestvideo[height<=720][vcodec^=avc1]+bestaudio[acodec^=mp4a]/bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]/best"
                opts["merge_output_format"] = "mp4"
            elif q in ("480p", "480", "sd"):
                opts["format"] = "bestvideo[height<=480][vcodec^=avc1]+bestaudio[acodec^=mp4a]/bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]/best"
                opts["merge_output_format"] = "mp4"
            elif q in ("360p", "360"):
                opts["format"] = "bestvideo[height<=360][vcodec^=avc1]+bestaudio[acodec^=mp4a]/bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]/best"
                opts["merge_output_format"] = "mp4"
            else:
                # Default: Best H.264 MP4 under 2GB (Telegram streamable)
                opts["format"] = "bestvideo[vcodec^=avc1][filesize<1900M]+bestaudio[acodec^=mp4a]/bestvideo[ext=mp4][filesize<1900M]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                opts["merge_output_format"] = "mp4"

            opts["ignoreerrors"] = False
            opts["postprocessor_args"] = {"Merger+ffmpeg": ["-movflags", "+faststart"]}
            _isolate_yt_dlp_plugins()

            has_cookies = bool(opts.get("cookiefile"))
            strategies = ([{"clients": ["web_embedded", "tv_samsung", "web"], "use_cookies": True}] if has_cookies else []) + [
                {"clients": ["tv_samsung", "web_safari"], "use_cookies": False},
                {"clients": ["android_vr", "ios", "visionos"], "use_cookies": False},
            ]
            info = None
            last_err = None
            for strat in strategies:
                s_opts = dict(opts)
                if not strat["use_cookies"]:
                    s_opts.pop("cookiefile", None)
                s_opts["extractor_args"] = {"youtube": {"player_client": strat["clients"]}}
                try:
                    with yt_dlp.YoutubeDL(s_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        if info:
                            video_filename = ydl.prepare_filename(info)
                            break
                except Exception as ex:
                    last_err = ex
            if not info:
                raise RuntimeError(f"Download failed for {url}: {last_err}")
            base_stem = Path(video_filename).stem
            final_video_path = None

            # Probe likely output paths
            candidates = [
                Path(video_filename),
                self.download_dir / f"{base_stem}.mp4",
                self.download_dir / f"{base_stem}.mkv",
                self.download_dir / f"{base_stem}.webm",
                self.download_dir / f"{base_stem}.mp3",
                self.download_dir / f"{base_stem}.m4a",
                self.download_dir / f"{base_stem}.aac",
                self.download_dir / f"{base_stem}.opus",
            ]
            for cand in candidates:
                if cand.is_file() and cand.stat().st_size > 0:
                    final_video_path = cand
                    break

            if not final_video_path:
                for f in self.download_dir.glob(f"{glob.escape(base_stem)}.*"):
                    if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".part", ".ytdl") and f.stat().st_size > 0:
                        final_video_path = f
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

        final_thumb = resolve_upload_thumbnail(thumb_path)
        return {
            "title": title,
            "uploader": uploader,
            "duration_sec": duration,
            "duration_str": format_duration(duration),
            "filesize": filesize,
            "filesize_str": format_bytes(filesize),
            "file_path": str(video_path),
            "thumb_path": str(final_thumb) if final_thumb else None,
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

            # HLS / .m3u8 direct stream remux via FFmpeg
            if is_hls_url(url) and self.ffmpeg_exe:
                mp4_out = target_path.with_suffix(".mp4")
                cmd = [
                    self.ffmpeg_exe, "-y", "-i", url,
                    "-c", "copy", "-bsf:a", "aac_adtstoasc", "-movflags", "+faststart",
                    str(mp4_out),
                ]
                proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE)
                _, err_b = await proc.communicate()
                if proc.returncode == 0 and mp4_out.is_file() and mp4_out.stat().st_size > 0:
                    fsize = mp4_out.stat().st_size
                    cov = resolve_upload_thumbnail(None)
                    return {
                        "title": mp4_out.stem,
                        "uploader": "HLS Stream",
                        "duration_sec": 0,
                        "duration_str": "N/A",
                        "filesize": fsize,
                        "filesize_str": format_bytes(fsize),
                        "file_path": str(mp4_out),
                        "thumb_path": str(cov) if cov else None,
                        "is_direct": True,
                        "url": url,
                    }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "*/*",
            }
            use_cffi = False
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=600)) as resp:
                if resp.status in (403, 429, 503):
                    use_cffi = True
                elif resp.status not in (200, 206):
                    raise ValueError(f"HTTP {resp.status} while downloading direct link: {url}")
                else:
                    ctype = (resp.headers.get("content-type") or "").lower()
                    if ctype.startswith("text/html") and not clean_name.lower().endswith(".html"):
                        use_cffi = True
                    else:
                        with open(target_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(65536):
                                if chunk:
                                    f.write(chunk)

            if use_cffi:
                from curl_cffi.requests import AsyncSession as CffiAsyncSession
                async with CffiAsyncSession(impersonate="chrome") as cs:
                    r = await cs.get(url, timeout=600)
                    if r.status_code not in (200, 206):
                        raise ValueError(f"HTTP {r.status_code} (curl_cffi) while downloading: {url}")
                    target_path.write_bytes(r.content)

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
        safe_t = html.escape(str(t_val))
        safe_u = html.escape(str(u_val))
        safe_d = html.escape(str(d_val))
        safe_tags = html.escape(str(tags))

        caption_lines = [
            f"{prefix}<b>{safe_t}</b>",
            "",
            f"👤 <b>Faculty / Channel:</b> <code>{safe_u}</code>",
            f"⏱️ <b>Duration:</b> <code>{safe_d}</code> | ⚡ <b>HD Stream</b>",
            "",
            f"🏷️ <i>{safe_tags}</i>",
            '📚 <a href="https://t.me/be_as_kind"><b>Kind Doctor &amp; Team</b></a> · 💬 <a href="https://t.me/KindDoc_bot"><b>Group Study Help 😉</b></a>',
        ]
        return "\n".join(caption_lines)


# Singleton Engine Instance
media_engine = MediaDownloaderEngine()
format_media_caption = MediaDownloaderEngine.format_media_caption
cleanup_files = MediaDownloaderEngine.cleanup_files
