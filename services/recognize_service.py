"""
Сервис распознавания музыки через shazamio.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from utils.logger import logger


async def recognize_track(audio_path: Path) -> Optional[dict]:
    """
    Распознаёт трек из аудиофайла через shazamio.
    Возвращает словарь с данными или None.
    """
    try:
        from shazamio import Shazam
        shazam = Shazam()
        result = await shazam.recognize(str(audio_path))
    except ImportError:
        logger.error("shazamio not installed. Run: pip install shazamio")
        return None
    except Exception as e:
        logger.error(f"Shazam recognition error: {e}")
        return None

    matches = result.get("matches", [])
    if not matches:
        return None

    track = result.get("track", {})
    if not track:
        return None

    title = track.get("title", "Unknown")
    artist = track.get("subtitle", "Unknown")

    # Thumbnail
    images = track.get("images", {})
    thumbnail = images.get("coverarthq") or images.get("coverart")

    # Duration (из sections/metadata)
    duration: Optional[int] = None
    for section in track.get("sections", []):
        if section.get("type") == "SONG":
            for meta in section.get("metadata", []):
                if meta.get("title") == "Duration":
                    try:
                        # Формат "3:45"
                        parts = meta["text"].split(":")
                        duration = int(parts[0]) * 60 + int(parts[1])
                    except Exception:
                        pass

    # Album
    album: Optional[str] = None
    for section in track.get("sections", []):
        if section.get("type") == "SONG":
            for meta in section.get("metadata", []):
                if meta.get("title") == "Album":
                    album = meta.get("text")

    # External links
    hub = track.get("hub", {})
    providers = hub.get("providers", [])
    spotify_url = None
    for provider in providers:
        if provider.get("type") == "SPOTIFY":
            actions = provider.get("actions", [])
            if actions:
                spotify_url = actions[0].get("uri")

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "duration": duration,
        "thumbnail": thumbnail,
        "spotify_url": spotify_url,
        "raw": result,
    }
