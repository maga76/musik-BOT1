"""
Сервис поиска и скачивания музыки через yt-dlp.
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yt_dlp

from config import settings
from utils.logger import logger


@dataclass
class TrackInfo:
    title: str
    artist: str
    duration: Optional[int] = None
    album: Optional[str] = None
    thumbnail: Optional[str] = None
    youtube_url: Optional[str] = None
    spotify_url: Optional[str] = None
    file_path: Optional[Path] = None
    source_url: Optional[str] = None
    extra: dict = field(default_factory=dict)


BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android"],
        }
    },
}


async def search_music(query: str) -> list[TrackInfo]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _search_sync, query)


def _search_sync(query: str) -> list[TrackInfo]:
    ydl_opts = {**BASE_OPTS, "extract_flat": True}
    search_query = query if query.startswith(("http://", "https://")) else f"ytsearch5:{query}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
    except Exception as e:
        logger.error(f"yt-dlp search error: {e}")
        return []

    entries = info.get("entries") or ([info] if info else [])
    results: list[TrackInfo] = []

    for entry in entries[:5]:
        if not entry:
            continue
        duration = entry.get("duration")
        if duration is not None:
            duration = int(duration)
        results.append(TrackInfo(
            title=entry.get("title") or "Unknown",
            artist=entry.get("artist") or entry.get("uploader") or "Unknown",
            duration=duration,
            thumbnail=entry.get("thumbnail"),
            youtube_url=entry.get("webpage_url") or entry.get("url"),
            source_url=entry.get("webpage_url"),
            album=entry.get("album"),
        ))

    return results


async def download_mp3(url: str, title: str = "audio", artist: str = "") -> Optional[Path]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _download_sync, url, title, artist)


def _download_sync(url: str, title: str = "audio", artist: str = "") -> Optional[Path]:
    uid = uuid.uuid4().hex[:8]
    out_template = str(settings.downloads_dir / f"track_{uid}.%(ext)s")

    # Сначала пробуем без ffmpeg — скачиваем m4a/webm напрямую
    ydl_opts = {
        **BASE_OPTS,
        "format": "bestaudio/best",  # m4a не требует ffmpeg
        "outtmpl": out_template,
        "max_filesize": settings.max_file_size_bytes,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            # Ищем скачанный файл
            for ext in ("m4a", "webm", "opus", "mp3", "ogg"):
                for f in settings.downloads_dir.glob(f"track_{uid}.{ext}"):
                    return f
    except Exception as e:
        logger.error(f"yt-dlp download error: {e}")
    return None
