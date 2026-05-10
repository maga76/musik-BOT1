"""
Модели базы данных (SQLAlchemy 2.x async).
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Boolean, DateTime, Enum, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class LanguageEnum(str, enum.Enum):
    RU = "ru"
    EN = "en"
    UZ = "uz"


class ImageStyleEnum(str, enum.Enum):
    REALISTIC = "realistic"
    ANIME = "anime"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    CINEMATIC = "cinematic"


class ImageSizeEnum(str, enum.Enum):
    SQUARE = "1024x1024"
    VERTICAL = "768x1344"
    HORIZONTAL = "1344x768"


# ─────────────────────────────────────────
# USERS
# ─────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(64))
    first_name: Mapped[str] = mapped_column(String(128), default="")
    last_name: Mapped[Optional[str]] = mapped_column(String(128))
    language: Mapped[LanguageEnum] = mapped_column(
        Enum(LanguageEnum), default=LanguageEnum.RU
    )
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    generations: Mapped[list["Generation"]] = relationship(back_populates="user")
    music_history: Mapped[list["MusicHistory"]] = relationship(back_populates="user")
    limits: Mapped[Optional["UserLimit"]] = relationship(back_populates="user", uselist=False)
    settings: Mapped[Optional["UserSettings"]] = relationship(back_populates="user", uselist=False)

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name


# ─────────────────────────────────────────
# GENERATIONS
# ─────────────────────────────────────────
class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    prompt: Mapped[str] = mapped_column(Text)
    style: Mapped[ImageStyleEnum] = mapped_column(
        Enum(ImageStyleEnum), default=ImageStyleEnum.REALISTIC
    )
    size: Mapped[ImageSizeEnum] = mapped_column(
        Enum(ImageSizeEnum), default=ImageSizeEnum.SQUARE
    )
    image_url: Mapped[Optional[str]] = mapped_column(Text)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="generations")


# ─────────────────────────────────────────
# MUSIC HISTORY
# ─────────────────────────────────────────
class MusicHistory(Base):
    __tablename__ = "music_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    query: Mapped[str] = mapped_column(Text)
    track_title: Mapped[Optional[str]] = mapped_column(String(256))
    track_artist: Mapped[Optional[str]] = mapped_column(String(256))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    action: Mapped[str] = mapped_column(String(32), default="search")  # search | recognize
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="music_history")


# ─────────────────────────────────────────
# USER LIMITS
# ─────────────────────────────────────────
class UserLimit(Base):
    __tablename__ = "limits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    image_count: Mapped[int] = mapped_column(Integer, default=0)
    music_count: Mapped[int] = mapped_column(Integer, default=0)
    recognize_count: Mapped[int] = mapped_column(Integer, default=0)
    reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="limits")


# ─────────────────────────────────────────
# USER SETTINGS
# ─────────────────────────────────────────
class UserSettings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True)
    default_style: Mapped[ImageStyleEnum] = mapped_column(
        Enum(ImageStyleEnum), default=ImageStyleEnum.REALISTIC
    )
    default_size: Mapped[ImageSizeEnum] = mapped_column(
        Enum(ImageSizeEnum), default=ImageSizeEnum.SQUARE
    )
    notifications: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped["User"] = relationship(back_populates="settings")
