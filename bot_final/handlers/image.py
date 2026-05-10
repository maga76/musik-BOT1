"""
Обработчик генерации изображений.
"""
from __future__ import annotations

import io

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from config import settings
from database import (
    AsyncSessionFactory, ImageSizeEnum, ImageStyleEnum,
    get_or_create_limits, increment_limit, reset_limits_if_needed, save_generation,
)
from keyboards import cancel_kb, size_kb, style_kb
from services import generate_image
from states import ImageGenStates

router = Router(name="image")

STYLE_LABELS = {
    "realistic": "🖼 Реалистичный",
    "anime": "🌸 Аниме",
    "cyberpunk": "🤖 Киберпанк",
    "fantasy": "🧙 Фэнтези",
    "cinematic": "🎬 Кинематограф",
}

SIZE_LABELS = {
    "1024x1024": "⬛ Квадрат",
    "768x1344": "📱 Вертикальный",
    "1344x768": "🖥 Горизонтальный",
}


async def check_image_limit(user_id: int) -> tuple[bool, int]:
    """Проверяет лимит генераций. Возвращает (allowed, remaining)."""
    async with AsyncSessionFactory() as session:
        lim = await get_or_create_limits(session, user_id)
        lim = await reset_limits_if_needed(session, lim)
        remaining = settings.RATE_LIMIT_IMAGE - lim.image_count
        return remaining > 0, max(0, remaining)


# ─────────────────────────────────────────
# СТАРТ ГЕНЕРАЦИИ
# ─────────────────────────────────────────

@router.message(Command("image"))
@router.message(F.text == "🎨 Генерация картинки")
async def cmd_image(message: Message, state: FSMContext) -> None:
    allowed, remaining = await check_image_limit(message.from_user.id)
    if not allowed:
        await message.answer(
            f"⛔ Лимит генераций исчерпан ({settings.RATE_LIMIT_IMAGE}/час).\n"
            "Попробуй через час."
        )
        return

    await state.set_state(ImageGenStates.waiting_prompt)
    await message.answer(
        "🎨 <b>Генерация изображения</b>\n\n"
        f"Осталось генераций: <b>{remaining}</b>\n\n"
        "Опиши, что хочешь увидеть (на любом языке):",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )


@router.message(ImageGenStates.waiting_prompt, F.text)
async def on_prompt(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отмена":
        await state.clear()
        from keyboards import main_menu_kb
        await message.answer("❌ Отменено.", reply_markup=main_menu_kb())
        return

    await state.update_data(prompt=message.text)
    await state.set_state(ImageGenStates.waiting_style)
    await message.answer(
        "🎨 Выбери <b>стиль</b> изображения:",
        reply_markup=style_kb(),
        parse_mode="HTML",
    )


# ─────────────────────────────────────────
# ВЫБОР СТИЛЯ
# ─────────────────────────────────────────

@router.callback_query(ImageGenStates.waiting_style, F.data.startswith("style:"))
async def on_style(callback: CallbackQuery, state: FSMContext) -> None:
    style_key = callback.data.split(":")[1]
    await state.update_data(style=style_key)
    await state.set_state(ImageGenStates.waiting_size)
    label = STYLE_LABELS.get(style_key, style_key)
    await callback.message.edit_text(
        f"✅ Стиль: <b>{label}</b>\n\n📐 Теперь выбери <b>размер</b>:",
        reply_markup=size_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ─────────────────────────────────────────
# ВЫБОР РАЗМЕРА И ГЕНЕРАЦИЯ
# ─────────────────────────────────────────

@router.callback_query(ImageGenStates.waiting_size, F.data.startswith("size:"))
async def on_size(callback: CallbackQuery, state: FSMContext) -> None:
    size_key = callback.data.split(":")[1]
    data = await state.get_data()
    prompt = data["prompt"]
    style_key = data.get("style", "realistic")

    await state.set_state(ImageGenStates.generating)
    size_label = SIZE_LABELS.get(size_key, size_key)
    style_label = STYLE_LABELS.get(style_key, style_key)

    await callback.message.edit_text(
        f"⏳ Генерирую...\n\n"
        f"📝 <i>{prompt}</i>\n"
        f"🎨 {style_label} | 📐 {size_label}",
        parse_mode="HTML",
    )
    await callback.answer()

    style = ImageStyleEnum(style_key)
    size = ImageSizeEnum(size_key)
    user_id = callback.from_user.id

    url, img_bytes = await generate_image(prompt, style, size)

    success = bool(url or img_bytes)
    async with AsyncSessionFactory() as session:
        await save_generation(
            session, user_id, prompt, style, size,
            image_url=url, success=success,
        )
        if success:
            await increment_limit(session, user_id, "image_count")

    if not success:
        await callback.message.answer(
            "❌ Не удалось сгенерировать изображение.\n"
            "Проверь API-ключи или попробуй позже."
        )
        await state.clear()
        return

    caption = (
        f"🎨 <b>{style_label}</b> | 📐 {size_label}\n"
        f"📝 {prompt}"
    )

    if url:
        # Скачиваем изображение и отправляем через Telegram
        async with aiohttp.ClientSession() as http:
            async with http.get(url) as resp:
                img_bytes = await resp.read()

    file = BufferedInputFile(img_bytes, filename="image.png")
    from keyboards import main_menu_kb
    await callback.message.answer_photo(
        file,
        caption=caption,
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
    await state.clear()
