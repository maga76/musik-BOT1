"""
Обработчики профиля и настроек.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import (
    AsyncSessionFactory, ImageSizeEnum, ImageStyleEnum,
    get_or_create_limits, get_or_create_settings, get_user_generations,
    get_user_music_history, reset_limits_if_needed, update_user_settings,
)
from keyboards import main_menu_kb, profile_kb, settings_kb, size_kb, style_kb
from states import SettingsStates
from utils.helpers import format_profile

router = Router(name="profile")


# ─────────────────────────────────────────
# ПРОФИЛЬ
# ─────────────────────────────────────────

@router.message(Command("profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message) -> None:
    user_id = message.from_user.id
    async with AsyncSessionFactory() as session:
        lim = await get_or_create_limits(session, user_id)
        lim = await reset_limits_if_needed(session, lim)
        gens = await get_user_generations(session, user_id, limit=999)
        music = await get_user_music_history(session, user_id, limit=999)

        from database import get_user
        user = await get_user(session, user_id)
        if not user:
            await message.answer("❌ Пользователь не найден.")
            return

        text = format_profile(user, lim, len(gens), len(music))

    await message.answer(text, reply_markup=profile_kb(), parse_mode="HTML")


@router.callback_query(F.data == "profile:gen_history")
async def on_gen_history(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    async with AsyncSessionFactory() as session:
        gens = await get_user_generations(session, user_id, limit=10)

    if not gens:
        await callback.answer("📭 История генераций пуста", show_alert=True)
        return

    lines = ["📸 <b>Последние генерации:</b>\n"]
    for i, g in enumerate(gens, 1):
        date = g.created_at.strftime("%d.%m %H:%M")
        lines.append(f"{i}. [{date}] <i>{g.prompt[:50]}</i> — {g.style.value}")

    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "profile:music_history")
async def on_music_history(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    async with AsyncSessionFactory() as session:
        history = await get_user_music_history(session, user_id, limit=10)

    if not history:
        await callback.answer("📭 История музыки пуста", show_alert=True)
        return

    lines = ["🎵 <b>История музыки:</b>\n"]
    for i, h in enumerate(history, 1):
        date = h.created_at.strftime("%d.%m %H:%M")
        track = f"{h.track_artist} — {h.track_title}" if h.track_title else h.query[:50]
        lines.append(f"{i}. [{date}] {track}")

    await callback.message.answer("\n".join(lines), parse_mode="HTML")
    await callback.answer()


# ─────────────────────────────────────────
# НАСТРОЙКИ
# ─────────────────────────────────────────

@router.message(Command("settings"))
@router.message(F.text == "⚙️ Настройки")
async def cmd_settings(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    async with AsyncSessionFactory() as session:
        s = await get_or_create_settings(session, user_id)

    notif = "🔔 Вкл" if s.notifications else "🔕 Выкл"
    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"🎨 Стиль по умолчанию: <b>{s.default_style.value}</b>\n"
        f"📐 Размер по умолчанию: <b>{s.default_size.value}</b>\n"
        f"Уведомления: <b>{notif}</b>"
    )
    await state.set_state(SettingsStates.main)
    await message.answer(text, reply_markup=settings_kb(), parse_mode="HTML")


@router.callback_query(SettingsStates.main, F.data == "settings:style")
async def on_settings_style(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsStates.choosing_style)
    await callback.message.edit_text(
        "🎨 Выбери стиль по умолчанию:",
        reply_markup=style_kb(),
    )
    await callback.answer()


@router.callback_query(SettingsStates.choosing_style, F.data.startswith("style:"))
async def on_settings_style_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    style_key = callback.data.split(":")[1]
    user_id = callback.from_user.id
    async with AsyncSessionFactory() as session:
        await update_user_settings(
            session, user_id, default_style=ImageStyleEnum(style_key)
        )
    await callback.message.edit_text(f"✅ Стиль по умолчанию: <b>{style_key}</b>", parse_mode="HTML")
    await state.set_state(SettingsStates.main)
    await callback.answer("Сохранено!")


@router.callback_query(SettingsStates.main, F.data == "settings:size")
async def on_settings_size(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SettingsStates.choosing_size)
    await callback.message.edit_text(
        "📐 Выбери размер по умолчанию:",
        reply_markup=size_kb(),
    )
    await callback.answer()


@router.callback_query(SettingsStates.choosing_size, F.data.startswith("size:"))
async def on_settings_size_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    size_key = callback.data.split(":")[1]
    user_id = callback.from_user.id
    async with AsyncSessionFactory() as session:
        await update_user_settings(
            session, user_id, default_size=ImageSizeEnum(size_key)
        )
    await callback.message.edit_text(f"✅ Размер по умолчанию: <b>{size_key}</b>", parse_mode="HTML")
    await state.set_state(SettingsStates.main)
    await callback.answer("Сохранено!")


@router.callback_query(SettingsStates.main, F.data == "settings:notifications")
async def on_settings_notifications(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    async with AsyncSessionFactory() as session:
        s = await get_or_create_settings(session, user_id)
        new_val = not s.notifications
        await update_user_settings(session, user_id, notifications=new_val)

    status = "🔔 включены" if new_val else "🔕 выключены"
    await callback.answer(f"Уведомления {status}!", show_alert=True)
