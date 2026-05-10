"""
bot.py — точка входа. Запускает aiogram бота в режиме long-polling.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database import init_db
from handlers import setup_routers
from middlewares import AntiSpamMiddleware, LoggingMiddleware, UserMiddleware
from utils.logger import logger

# ─────────────────────────────────────────
# Глобальный экземпляр бота (используется в handlers/recognize.py)
# ─────────────────────────────────────────
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def main() -> None:
    # Инициализируем БД
    await init_db()
    logger.info("Database initialized.")

    # Создаём dispatcher
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Регистрируем middleware (порядок важен!)
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(AntiSpamMiddleware(throttle_time=0.7))
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # Подключаем все роутеры
    dp.include_router(setup_routers())

    logger.info("Starting bot polling...")

    # Удаляем webhook на всякий случай
    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
