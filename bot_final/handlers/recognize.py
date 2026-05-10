"""
Распознавание музыки — недоступно на Python 3.14.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router(name="recognize")


@router.message(Command("recognize"))
@router.message(F.text == "🔍 Распознать музыку")
async def cmd_recognize(message: Message, state: FSMContext) -> None:
    await message.answer(
        "⚠️ Функция распознавания музыки недоступна.\n\n"
        "Используй бота <b>@VoiceShazamBot</b> — он отлично справляется с этим!",
        parse_mode="HTML",
    )