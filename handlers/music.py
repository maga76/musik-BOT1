"""
Обработчик поиска музыки — отправляет аудио сразу как в VoiceShazamBot.
"""
from __future__ import annotations

from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from config import settings
from database import AsyncSessionFactory, increment_limit, save_music_history
from keyboards import cancel_kb, main_menu_kb
from services import TrackInfo, download_mp3, search_music
from states import MusicSearchStates

router = Router(name="music")


async def check_music_limit(user_id: int) -> bool:
    from database import get_or_create_limits, reset_limits_if_needed
    async with AsyncSessionFactory() as session:
        lim = await get_or_create_limits(session, user_id)
        lim = await reset_limits_if_needed(session, lim)
        return lim.music_count < settings.RATE_LIMIT_MUSIC


@router.message(Command("music"))
@router.message(F.text == "🎵 Найти музыку")
async def cmd_music(message: Message, state: FSMContext) -> None:
    if not await check_music_limit(message.from_user.id):
        await message.answer(f"⛔ Лимит поиска исчерпан ({settings.RATE_LIMIT_MUSIC}/час).")
        return

    await state.set_state(MusicSearchStates.waiting_query)
    await message.answer(
        "🎵 <b>Поиск музыки</b>\n\n"
        "Введи название трека или исполнителя:",
        reply_markup=cancel_kb(),
        parse_mode="HTML",
    )


@router.message(MusicSearchStates.waiting_query, F.text)
async def on_music_query(message: Message, state: FSMContext) -> None:
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Отменено.", reply_markup=main_menu_kb())
        return

    query = message.text.strip()
    wait_msg = await message.answer("🔍 Ищу музыку...")

    tracks = await search_music(query)

    if not tracks:
        await wait_msg.edit_text("❌ Ничего не найдено. Попробуй другой запрос.")
        return

    track = tracks[0]

    await wait_msg.edit_text(
        f"⬇️ Скачиваю: <b>{track.title}</b> — {track.artist}...",
        parse_mode="HTML",
    )

    # Сохраняем в БД
    async with AsyncSessionFactory() as session:
        await save_music_history(
            session, message.from_user.id, query,
            action="search",
            track_title=track.title,
            track_artist=track.artist,
            source_url=track.source_url,
        )
        await increment_limit(session, message.from_user.id, "music_count")

    # Скачиваем и отправляем
    file_path: Path | None = await download_mp3(
        track.source_url or track.youtube_url or "",
        title=track.title,
        artist=track.artist,
    )

    if not file_path or not file_path.exists():
        await wait_msg.edit_text(
            f"❌ Не удалось скачать трек.\n\n"
            f"▶️ Слушай на YouTube: {track.youtube_url}"
        )
        await state.clear()
        return

    try:
        audio_file = FSInputFile(file_path, filename=f"{track.artist} - {track.title}.m4a")
        await wait_msg.delete()
        await message.answer_audio(
            audio_file,
            title=track.title,
            performer=track.artist,
            duration=track.duration,
            thumbnail=None,
            reply_markup=main_menu_kb(),
        )
    except Exception as e:
        await wait_msg.edit_text(f"❌ Ошибка при отправке: {e}")
    finally:
        if file_path and file_path.exists():
            file_path.unlink(missing_ok=True)

    await state.clear()
