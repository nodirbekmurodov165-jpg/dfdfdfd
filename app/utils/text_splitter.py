import logging
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message

logger = logging.getLogger(__name__)

TELEGRAM_MAX_MESSAGE_LENGTH = 4000  # 4096 limitdan xavfsiz zaxira bilan


def split_message(text: str, max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    """
    Telegramning 4096 belgilik chekloviga moslashish uchun uzun matnlarni
    mantiqiy bo'laklarga (abzas, qator yoki so'z bo'yicha) ajratadi.
    """
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        # Bo'lish uchun eng qulay joyni qidiramiz: abzas -> yangi qator -> bo'sh joy
        split_idx = -1
        for separator in ("\n\n", "\n", " "):
            idx = remaining.rfind(separator, 0, max_length)
            if idx > max_length // 3:
                split_idx = idx + len(separator)
                break

        if split_idx == -1:
            split_idx = max_length

        chunk = remaining[:split_idx].rstrip()
        if chunk:
            chunks.append(chunk)
        remaining = remaining[split_idx:].lstrip()

    return chunks


async def send_chunked_message(message: Message, text: str) -> None:
    """
    Matnni bo'laklarga ajratib yuboradi. Agar Markdown formatlashda xatolik bo'lsa,
    avtomatik ravishda oddiy matn (plain text) sifatida yuboradi.
    """
    chunks = split_message(text)
    for chunk in chunks:
        try:
            await message.answer(chunk, parse_mode=ParseMode.MARKDOWN)
        except TelegramBadRequest:
            await message.answer(chunk, parse_mode=None)
