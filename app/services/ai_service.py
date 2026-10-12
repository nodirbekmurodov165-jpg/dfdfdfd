import logging
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
    """OpenAI API bilan asinxron muloqot va kontekst boshqaruvi."""

    def __init__(self, config: Config, db: Database) -> None:
        self.config = config
        self.db = db
        self.client = AsyncOpenAI(
            api_key=config.openai_api_key,
            base_url=config.openai_base_url,
            timeout=60.0,
            max_retries=2,
        )

    async def generate_reply(self, user_id: int, user_text: str) -> str:
        """
        Foydalanuvchi xabarini kontekst bilan birga OpenAI modeliga yuboradi
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

            if not reply_text:
                return "⚠️ Kechirasiz, AI bo'sh javob qaytardi. Iltimos, savolingizni boshqacharoq yozib ko'ring."

            # Muvaffaqiyatli javob olingach, foydalanuvchi xabari va AI javobini bazaga saqlaymiz
            await self.db.add_message(user_id=user_id, role="user", content=user_text)
            await self.db.add_message(user_id=user_id, role="assistant", content=reply_text)

            return reply_text

        except AuthenticationError as exc:
            logger.error("OpenAI AuthenticationError: %s", exc)
            return "❌ AI xizmatiga ulanishda avtorizatsiya xatosi yuz berdi (API kalit noto'g'ri)."

        except RateLimitError as exc:
            logger.warning("OpenAI RateLimitError (user_id=%s): %s", user_id, exc)
            return "⏳ So'rovlar limiti oshib ketdi yoki balans tugagan. Iltimos, birozdan so'ng qayta urinib ko'ring."

        except (APITimeoutError, APIConnectionError) as exc:
            logger.warning("OpenAI tarmoq/vaqt xatosi (user_id=%s): %s", user_id, exc)
            return "🌐 AI serveri bilan bog'lanishda uzilish yuz berdi. Iltimos, qaytadan urinib ko'ring."

        except APIError as exc:
            logger.error("OpenAI APIError (user_id=%s): %s", user_id, exc)
            return "⚠️ AI xizmatida vaqtinchalik xatolik yuz berdi. Iltimos, birozdan keyin qayta yozing."

        except Exception as exc:
            logger.exception("Kutilmagan AI xatosi (user_id=%s): %s", user_id, exc)
            return "❌ Javob tayyorlashda kutilmagan xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring."
