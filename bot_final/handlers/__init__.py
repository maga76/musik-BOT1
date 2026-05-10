from aiogram import Router

from .start import router as start_router
from .image import router as image_router
from .music import router as music_router
from .recognize import router as recognize_router
from .profile import router as profile_router


def setup_routers() -> Router:
    main_router = Router()
    main_router.include_router(start_router)
    main_router.include_router(image_router)
    main_router.include_router(music_router)
    main_router.include_router(recognize_router)
    main_router.include_router(profile_router)
    return main_router


__all__ = ["setup_routers"]
