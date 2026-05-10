"""
Клавиатуры для бота.
"""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


# ─────────────────────────────────────────
# ГЛАВНОЕ МЕНЮ
# ─────────────────────────────────────────

def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🎨 Генерация картинки"),
        KeyboardButton(text="🎵 Найти музыку"),
    )
    builder.row(
        KeyboardButton(text="🔍 Распознать музыку"),
        KeyboardButton(text="👤 Профиль"),
    )
    builder.row(
        KeyboardButton(text="⚙️ Настройки"),
        KeyboardButton(text="🌐 Язык"),
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ─────────────────────────────────────────
# ОТМЕНА
# ─────────────────────────────────────────

def cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


# ─────────────────────────────────────────
# СТИЛЬ ИЗОБРАЖЕНИЯ
# ─────────────────────────────────────────

def style_kb() -> InlineKeyboardMarkup:
    styles = [
        ("🖼 Реалистичный", "style:realistic"),
        ("🌸 Аниме", "style:anime"),
        ("🤖 Киберпанк", "style:cyberpunk"),
        ("🧙 Фэнтези", "style:fantasy"),
        ("🎬 Кинематограф", "style:cinematic"),
    ]
    builder = InlineKeyboardBuilder()
    for label, data in styles:
        builder.button(text=label, callback_data=data)
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()


# ─────────────────────────────────────────
# РАЗМЕР ИЗОБРАЖЕНИЯ
# ─────────────────────────────────────────

def size_kb() -> InlineKeyboardMarkup:
    sizes = [
        ("⬛ Квадрат (1024×1024)", "size:1024x1024"),
        ("📱 Вертикальный (768×1344)", "size:768x1344"),
        ("🖥 Горизонтальный (1344×768)", "size:1344x768"),
    ]
    builder = InlineKeyboardBuilder()
    for label, data in sizes:
        builder.button(text=label, callback_data=data)
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()


# ─────────────────────────────────────────
# РЕЗУЛЬТАТ МУЗЫКИ
# ─────────────────────────────────────────

def music_result_kb(
    spotify_url: str | None = None,
    youtube_url: str | None = None,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬇️ Скачать MP3", callback_data="music:download")
    if spotify_url:
        builder.button(text="🟢 Spotify", url=spotify_url)
    if youtube_url:
        builder.button(text="▶️ YouTube", url=youtube_url)
    builder.button(text="🔎 Найти похожее", callback_data="music:similar")
    builder.adjust(2)
    return builder.as_markup()


# ─────────────────────────────────────────
# ЯЗЫК
# ─────────────────────────────────────────

def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🇷🇺 Русский", callback_data="lang:ru")
    builder.button(text="🇬🇧 English", callback_data="lang:en")
    builder.button(text="🇺🇿 O'zbek", callback_data="lang:uz")
    builder.adjust(1)
    return builder.as_markup()


# ─────────────────────────────────────────
# НАСТРОЙКИ
# ─────────────────────────────────────────

def settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎨 Стиль по умолчанию", callback_data="settings:style")
    builder.button(text="📐 Размер по умолчанию", callback_data="settings:size")
    builder.button(text="🔔 Уведомления", callback_data="settings:notifications")
    builder.adjust(1)
    return builder.as_markup()


# ─────────────────────────────────────────
# ПРОФИЛЬ
# ─────────────────────────────────────────

def profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 История генераций", callback_data="profile:gen_history")
    builder.button(text="🎵 История музыки", callback_data="profile:music_history")
    builder.adjust(1)
    return builder.as_markup()
