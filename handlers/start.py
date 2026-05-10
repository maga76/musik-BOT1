"""
Обработчики /start, /help и главного меню.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards import language_kb, main_menu_kb
from utils.helpers import format_help

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    user = message.from_user
    text = (
        f"👋 <b>Привет, {user.first_name}!</b>\n\n"
        "Я умею:\n"
        "🎨 <b>Генерировать изображения</b> по описанию\n"
        "🎵 <b>Искать музыку</b> по названию или ссылке\n"
        "🔍 <b>Распознавать треки</b> из видео\n\n"
        "Выбери нужный раздел 👇"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.message(Command("help"))
@router.message(F.text == "❓ Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(format_help(), parse_mode="HTML")


@router.message(F.text == "🌐 Язык")
@router.message(Command("language"))
async def cmd_language(message: Message) -> None:
    await message.answer(
        "🌐 <b>Выбери язык / Choose language:</b>",
        reply_markup=language_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(callback: CallbackQuery) -> None:
    lang = callback.data.split(":")[1]
    lang_names = {"ru": "🇷🇺 Русский", "en": "🇬🇧 English", "uz": "🇺🇿 O'zbek"}
    name = lang_names.get(lang, lang)
    await callback.message.edit_text(f"✅ Язык изменён на <b>{name}</b>", parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def on_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Отменено.")
    await callback.answer()
