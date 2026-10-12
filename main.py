import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ErrorEvent

from app.config import load_config
from app.database import Database
from app.handlers import setup_routers
from app.services.ai_service import AIService

BASE_DIR = Path(__file__).resolve().parent


def setup_logging() -> None:
    """Konsol va fayl uchun log yozish tizimini sozlaydi (24/7 monitoring uchun)."""
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format)

    file_handler = RotatingFileHandler(
        log_dir / "bot.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


async def set_bot_commands(bot: Bot) -> None:
    """Telegram menyusidagi asosiy buyruqlarni o'rnatadi."""
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="clear", description="Suhbat tarixini tozalash"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
        BotCommand(command="about", description="Bot haqida ma'lumot"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        config = load_config()
    except ValueError as err:
        logger.error("Sozlamalar xatosi: %s", err)
        return

    # Ma'lumotlar bazasi va AI xizmatini ishga tushiramiz
    db = Database(str(BASE_DIR / config.db_path))
    await db.init_db()

    ai_service = AIService(config=config, db=db)

    dp = Dispatcher()

    # Dependency injection: handlerlarga obyektlarni uzatish
    dp["config"] = config
    dp["db"] = db
    dp["ai_service"] = ai_service

    # Global xatoliklarni ushlash (24/7 uzluksiz ishlash uchun)
    @dp.errors()
    async def global_error_handler(event: ErrorEvent) -> bool:
        logger.exception("Handler xatosi yuz berdi: %s", event.exception)
        if event.update.message:
            try:
                await event.update.message.answer(
                    "⚠️ So'rovni bajarishda kutilmagan xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
                )
            except Exception:
                pass
        return True

    dp.include_router(setup_routers())

    # 24/7 uzluksiz qayta ulanish sikli (internet uzilsa ham to'xtab qolmaydi)
    while True:
        bot = Bot(token=config.bot_token)
        try:
            await set_bot_commands(bot)
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("Telegram AI Chatbot 24/7 rejimida ishga tushdi!")
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                close_bot_session=True,
            )
            break
        except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
            logger.info("Bot to'xtatilmoqda...")
            break
        except Exception as exc:
            logger.error("Polling xatosi yuz berdi: %s. 5 soniyadan so'ng qayta ulanadi...", exc)
            await asyncio.sleep(5)
        finally:
            try:
                await bot.session.close()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
