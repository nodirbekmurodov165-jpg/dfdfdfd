import asyncio
import logging
import random
import httpx
from openai import (
    AsyncOpenAI,
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)
from app.config import Config
from app.database import Database

logger = logging.getLogger(__name__)


class AIService:
    """OpenAI API va zaxira AI shlyuzi bilan asinxron muloqot va kontekst boshqaruvi."""

    def __init__(self, config: Config, db: Database) -> None:
        self.config = config
        self.db = db
        self._gateway_lock = asyncio.Lock()
        self.client: AsyncOpenAI | None = None
        if config.openai_api_key:
            self.client = AsyncOpenAI(
                api_key=config.openai_api_key,
                base_url=config.openai_base_url,
                timeout=60.0,
                max_retries=2,
            )

    async def _call_free_ai_gateway(self, messages: list[dict[str, str]]) -> str:
        """
        Shaxsiy OpenAI API kaliti bo'lmaganda yoki u ishlamaganda
        uzluksiz 24/7 javob beruvchi AI shlyuzi.
        """
        last_error: Exception | None = None
        async with self._gateway_lock:
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as http_client:
                for attempt in range(5):
                    payload = {
                        "messages": messages,
                        "model": "openai-fast",
                        "seed": random.randint(1, 999999),
                    }
                    try:
                        resp = await http_client.post(
                            "https://text.pollinations.ai/",
                            json=payload,
                        )
                        if resp.status_code == 200 and resp.text.strip():
                            text = resp.text.strip()
                            # Maxfiy bo'sh belgilarni tozalaymiz
                            return text.replace("\u202f", " ").replace("\u200b", "")
                        logger.warning(
                            "AI gateway status=%s (urinish %s/5)",
                            resp.status_code,
                            attempt + 1,
                        )
                    except Exception as exc:
                        last_error = exc
                        logger.warning("AI gateway ulanish xatosi (urinish %s/5): %s", attempt + 1, exc)

                    await asyncio.sleep(3.5)

        if last_error:
            raise last_error
        raise RuntimeError("AI gateway javob qaytarmadi")

    async def generate_reply(self, user_id: int, user_text: str) -> str:
        """
        Foydalanuvchi xabarini kontekst bilan birga AI modeliga yuboradi
        va javobni ma'lumotlar bazasiga saqlab qaytaradi.
        """
        history = await self.db.get_context_messages(
            user_id=user_id,
            max_messages=self.config.max_context_messages,
            max_chars=self.config.max_context_chars,
        )

        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.config.system_prompt},
            *history,
            {"role": "user", "content": user_text},
        ]

        reply_text = ""

        # 1. Agar foydalanuvchi shaxsiy OPENAI_API_KEY kiritgan bo'lsa, avval uni ishlatamiz
        if self.client is not None:
            try:
                response = await self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=messages,  # type: ignore[arg-type]
                    temperature=0.7,
                )
                reply_text = (
                    response.choices[0].message.content
                    if response.choices and response.choices[0].message.content
                    else ""
                ).strip()
            except (AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError, APIError) as exc:
                logger.warning("Asosiy OpenAI API xatosi, zaxira AI shlyuzga o'tilmoqda: %s", exc)
            except Exception as exc:
                logger.warning("OpenAI kutilmagan xato, zaxira AI shlyuzga o'tilmoqda: %s", exc)

        # 2. Agar kalit kiritilmagan bo'lsa yoki asosiy API javob bermasa, zaxira shlyuz orqali olamiz
        if not reply_text:
            try:
                reply_text = await self._call_free_ai_gateway(messages)
            except Exception as exc:
                logger.exception("AI javob olishda xatolik (user_id=%s): %s", user_id, exc)
                return "🌐 AI serveri bilan bog'lanishda vaqtinchalik uzilish yuz berdi. Iltimos, qaytadan yozib ko'ring."

        if not reply_text:
            return "⚠️ Kechirasiz, AI bo'sh javob qaytardi. Iltimos, savolingizni boshqacharoq yozib ko'ring."

        # Muvaffaqiyatli javob olingach, foydalanuvchi xabari va AI javobini bazaga saqlaymiz
        await self.db.add_message(user_id=user_id, role="user", content=user_text)
        await self.db.add_message(user_id=user_id, role="assistant", content=reply_text)

        return reply_text
