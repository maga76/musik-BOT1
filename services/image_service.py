"""
Сервис генерации изображений через Pollinations AI (бесплатно, без API ключа).
"""
from __future__ import annotations

import urllib.parse

import aiohttp

from database.models import ImageSizeEnum, ImageStyleEnum
from utils.logger import logger

STYLE_SUFFIXES: dict[ImageStyleEnum, str] = {
    ImageStyleEnum.REALISTIC: "photorealistic, ultra-detailed, 8k, RAW photo",
    ImageStyleEnum.ANIME: "anime style, Studio Ghibli, vibrant colors, cel shading",
    ImageStyleEnum.CYBERPUNK: "cyberpunk, neon lights, dark city, futuristic, blade runner",
    ImageStyleEnum.FANTASY: "fantasy art, magical, epic, detailed illustration, artstation",
    ImageStyleEnum.CINEMATIC: "cinematic, dramatic lighting, movie still, anamorphic lens",
}

SIZE_MAP: dict[ImageSizeEnum, tuple[int, int]] = {
    ImageSizeEnum.SQUARE: (1024, 1024),
    ImageSizeEnum.VERTICAL: (768, 1344),
    ImageSizeEnum.HORIZONTAL: (1344, 768),
}


async def generate_image(
    prompt: str,
    style: ImageStyleEnum = ImageStyleEnum.REALISTIC,
    size: ImageSizeEnum = ImageSizeEnum.SQUARE,
) -> tuple[str | None, bytes | None]:
    """
    Генерирует изображение через Pollinations AI (бесплатно).
    Возвращает (url, image_bytes).
    """
    suffix = STYLE_SUFFIXES.get(style, "")
    full_prompt = f"{prompt}, {suffix}".strip(", ")
    encoded = urllib.parse.quote(full_prompt)

    w, h = SIZE_MAP.get(size, (1024, 1024))

    url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true&enhance=true"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as resp:
                if resp.status != 200:
                    logger.error(f"Pollinations error {resp.status}")
                    return None, None
                img_bytes = await resp.read()
                return None, img_bytes
    except Exception as e:
        logger.exception(f"Pollinations generation failed: {e}")
        return None, None
