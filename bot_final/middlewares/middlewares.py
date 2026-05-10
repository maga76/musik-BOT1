"""
Middleware: антиспам, rate-limit, регистрация пользователя.
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update

from config import settings
from database import AsyncSessionFactory, get_or_create_user, get_user
from utils.logger import logger


# ─────────────────────────────────────────
# USER REGISTRATION MIDDLEWARE
# ─────────────────────────────────────────

class UserMiddleware(BaseMiddleware):
    """Регистрирует пользователя при каждом обращении и добавляет сессию в data."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        async with AsyncSessionFactory() as session:
            db_user, created = await get_or_create_user(
                session=session,
                user_id=user.id,
                username=user.username,
                first_name=user.first_name or "",
                last_name=user.last_name,
                is_admin=user.id in settings.ADMIN_IDS,
            )
            if created:
                logger.info(f"New user registered: {user.id} @{user.username}")

            if db_user.is_banned:
                if isinstance(event, Message):
                    await event.answer("🚫 Вы заблокированы в боте.")
                return

            data["db_user"] = db_user
            data["session"] = session
            return await handler(event, data)


# ─────────────────────────────────────────
# ANTI-SPAM MIDDLEWARE
# ─────────────────────────────────────────

class AntiSpamMiddleware(BaseMiddleware):
    """Защита от флуда: не более 1 сообщения в секунду на пользователя."""

    def __init__(self, throttle_time: float = 1.0) -> None:
        super().__init__()
        self.throttle_time = throttle_time
        self._last_message: dict[int, float] = defaultdict(float)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last_message[user.id]
        if now - last < self.throttle_time:
            if isinstance(event, Message):
                await event.answer("⏳ Не так быстро! Подождите секунду.")
            return

        self._last_message[user.id] = now
        return await handler(event, data)


# ─────────────────────────────────────────
# LOGGING MIDDLEWARE
# ─────────────────────────────────────────

class LoggingMiddleware(BaseMiddleware):
    """Логирует входящие события."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user and isinstance(event, Message):
            logger.debug(
                f"[MSG] user={user.id} text={event.text!r:.80}"
                if event.text
                else f"[MSG] user={user.id} type={event.content_type}"
            )
        return await handler(event, data)
