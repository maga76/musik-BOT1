from __future__ import annotations
import re
from datetime import datetime, timezone
from typing import Optional


def format_profile(user, limits, gens_count: int, music_count: int) -> str:
    joined = user.created_at.strftime("%d.%m.%Y") if user.created_at else "—"
    return (
        f"👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"👤 Имя: {user.full_name}\n"
        f"📅 Дата регистрации: {joined}\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"🎨 Генераций: <b>{gens_count}</b>\n"
        f"🎵 Музыки найдено: <b>{music_count}</b>\n\n"
        f"⏱ <b>Лимиты (в час):</b>\n"
        f"🎨 Изображения: <b>{limits.image_count}</b> использовано\n"
        f"🎵 Музыка: <b>{limits.music_count}</b> использовано\n"
        f"🔍 Распознавание: <b>{limits.recognize_count}</b> использовано"
    )


def format_track_info(
    title: str,
    artist: str,
    duration: Optional[int] = None,
    album: Optional[str] = None,
) -> str:
    lines = [
        f"🎵 <b>{title}</b>",
        f"👤 Исполнитель: {artist}",
    ]
    if album:
        lines.append(f"💿 Альбом: {album}")
    if duration:
        duration = int(duration)
        m, s = divmod(duration, 60)
        lines.append(f"⏱ Длительность: {m}:{s:02d}")
    return "\n".join(lines)


def format_help() -> str:
    return (
        "📖 <b>Помощь</b>\n\n"
        "<b>Команды:</b>\n"
        "/start — главное меню\n"
        "/image — генерация изображения\n"
        "/music — поиск музыки\n"
        "/recognize — распознать музыку\n"
        "/profile — мой профиль\n"
        "/settings — настройки\n"
        "/help — эта справка\n\n"
        "<b>Поиск музыки:</b> введи название трека или исполнителя.\n"
        "<b>Генерация:</b> опиши что хочешь увидеть."
    )


VIDEO_URL_PATTERNS = [
    re.compile(r"https?://(www\.)?(youtube\.com|youtu\.be)/\S+"),
    re.compile(r"https?://(www\.)?tiktok\.com/\S+"),
    re.compile(r"https?://(www\.)?instagram\.com/(reel|p)/\S+"),
]


def is_video_url(text: str) -> bool:
    return any(p.match(text.strip()) for p in VIDEO_URL_PATTERNS)


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)[:128]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
