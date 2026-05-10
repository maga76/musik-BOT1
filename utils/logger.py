"""
Настройка логирования.
"""
import logging
import sys
from pathlib import Path

from config import settings


def setup_logger() -> logging.Logger:
    log_dir = settings.logs_dir
    log_file = log_dir / "bot.log"

    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding="utf-8"),
    ]

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=fmt,
        datefmt=date_fmt,
        handlers=handlers,
    )

    # Заглушить слишком шумные либы
    for noisy in ("aiohttp", "aiogram.event", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return logging.getLogger("bot")


logger = setup_logger()
