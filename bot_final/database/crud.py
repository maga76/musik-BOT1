"""
CRUD-операции для всех таблиц.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    Generation, ImageSizeEnum, ImageStyleEnum,
    LanguageEnum, MusicHistory, User, UserLimit, UserSettings,
)


# ─────────────────────────────────────────
# USERS
# ─────────────────────────────────────────

async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    username: Optional[str],
    first_name: str,
    last_name: Optional[str],
    is_admin: bool = False,
) -> tuple[User, bool]:
    """Возвращает (user, created)."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        # Обновляем имя/username
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        await session.commit()
        return user, False

    user = User(
        id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        is_admin=is_admin,
    )
    session.add(user)

    # Создаём лимиты и настройки вместе с пользователем
    session.add(UserLimit(user_id=user_id))
    session.add(UserSettings(user_id=user_id))

    await session.commit()
    await session.refresh(user)
    return user, True


async def get_user(session: AsyncSession, user_id: int) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def set_user_language(
    session: AsyncSession, user_id: int, lang: LanguageEnum
) -> None:
    await session.execute(
        update(User).where(User.id == user_id).values(language=lang)
    )
    await session.commit()


# ─────────────────────────────────────────
# LIMITS
# ─────────────────────────────────────────

async def get_or_create_limits(session: AsyncSession, user_id: int) -> UserLimit:
    result = await session.execute(
        select(UserLimit).where(UserLimit.user_id == user_id)
    )
    lim = result.scalar_one_or_none()
    if not lim:
        lim = UserLimit(user_id=user_id)
        session.add(lim)
        await session.commit()
        await session.refresh(lim)
    return lim


async def reset_limits_if_needed(session: AsyncSession, lim: UserLimit) -> UserLimit:
    """Сбрасывает счётчики, если прошёл час."""
    now = datetime.now(timezone.utc)
    reset_at = lim.reset_at.replace(tzinfo=timezone.utc) if lim.reset_at.tzinfo is None else lim.reset_at
    if now - reset_at >= timedelta(hours=1):
        lim.image_count = 0
        lim.music_count = 0
        lim.recognize_count = 0
        lim.reset_at = now
        await session.commit()
        await session.refresh(lim)
    return lim


async def increment_limit(
    session: AsyncSession, user_id: int, field: str
) -> None:
    lim = await get_or_create_limits(session, user_id)
    lim = await reset_limits_if_needed(session, lim)
    setattr(lim, field, getattr(lim, field) + 1)
    await session.commit()


# ─────────────────────────────────────────
# GENERATIONS
# ─────────────────────────────────────────

async def save_generation(
    session: AsyncSession,
    user_id: int,
    prompt: str,
    style: ImageStyleEnum,
    size: ImageSizeEnum,
    image_url: Optional[str] = None,
    success: bool = True,
) -> Generation:
    gen = Generation(
        user_id=user_id,
        prompt=prompt,
        style=style,
        size=size,
        image_url=image_url,
        success=success,
    )
    session.add(gen)
    await session.commit()
    await session.refresh(gen)
    return gen


async def get_user_generations(
    session: AsyncSession, user_id: int, limit: int = 10
) -> list[Generation]:
    result = await session.execute(
        select(Generation)
        .where(Generation.user_id == user_id)
        .order_by(Generation.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars())


# ─────────────────────────────────────────
# MUSIC HISTORY
# ─────────────────────────────────────────

async def save_music_history(
    session: AsyncSession,
    user_id: int,
    query: str,
    action: str = "search",
    track_title: Optional[str] = None,
    track_artist: Optional[str] = None,
    source_url: Optional[str] = None,
) -> MusicHistory:
    entry = MusicHistory(
        user_id=user_id,
        query=query,
        action=action,
        track_title=track_title,
        track_artist=track_artist,
        source_url=source_url,
    )
    session.add(entry)
    await session.commit()
    return entry


async def get_user_music_history(
    session: AsyncSession, user_id: int, limit: int = 10
) -> list[MusicHistory]:
    result = await session.execute(
        select(MusicHistory)
        .where(MusicHistory.user_id == user_id)
        .order_by(MusicHistory.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars())


# ─────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────

async def get_or_create_settings(
    session: AsyncSession, user_id: int
) -> UserSettings:
    result = await session.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    s = result.scalar_one_or_none()
    if not s:
        s = UserSettings(user_id=user_id)
        session.add(s)
        await session.commit()
        await session.refresh(s)
    return s


async def update_user_settings(
    session: AsyncSession,
    user_id: int,
    **kwargs,
) -> UserSettings:
    s = await get_or_create_settings(session, user_id)
    for k, v in kwargs.items():
        setattr(s, k, v)
    await session.commit()
    await session.refresh(s)
    return s
