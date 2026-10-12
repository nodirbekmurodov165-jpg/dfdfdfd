import asyncio
import logging
import os
import socket
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import httpx
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, ErrorEvent

from app.config import load_config
from app.database import Database
from app.handlers import setup_routers
from app.services.ai_service import AIService

BASE_DIR = Path(__file__).resolve().parent
SINGLE_INSTANCE_PORT = 48914


def acquire_single_instance_lock() -> socket.socket | None:
    """
    Bir vaqtning o'zida ikkita bot nusxasi ishga tushib TelegramConflictError
    bermasligi uchun lokal port orqali blokirovka (lock) oladi.
    """
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lock_socket.bind(("127.0.0.1", SINGLE_INSTANCE_PORT))
        lock_socket.listen(1)
        return lock_socket
    except OSError:
        lock_socket.close()
        return None


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


async def start_health_server() -> web.AppRunner | None:
    """
    Render.com Web Service port tekshiruvidan ('No open ports detected')
    muvaffaqiyatli o'tishi uchun yengil HTTP serverni ishga tushiradi.
    """
    port_str = os.getenv("PORT", "")
    if not port_str and not os.getenv("RENDER"):
        return None

    port = int(port_str or "10000")

    async def handle_health(_request: web.Request) -> web.Response:
        return web.Response(text="Telegram AI Chatbot 24/7 is running!", status=200)

    web_app = web.Application()
    web_app.router.add_get("/", handle_health)
    web_app.router.add_get("/health", handle_health)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logging.getLogger(__name__).info("Render Health HTTP server 0.0.0.0:%s portda ishga tushdi.", port)
    return runner


async def render_keep_alive_loop() -> None:
    """Render Free Tier uyquga ketmasligi uchun har 10 daqiqada o'zini ping qilib turadi."""
    external_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if not external_url:
        return

    ping_url = f"{external_url.rstrip('/')}/health"
    async with httpx.AsyncClient(timeout=15.0) as client:
        while True:
            await asyncio.sleep(600)
            try:
                await client.get(ping_url)
            except Exception:
                pass


async def run_bot(start_web: bool = True) -> None:
    lock_socket = acquire_single_instance_lock()
    if lock_socket is None:
        sys.exit(0)

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        config = load_config()
    except ValueError as err:
        logger.error("Sozlamalar xatosi: %s", err)
        return

    db = Database(str(BASE_DIR / config.db_path))
    await db.init_db()

    ai_service = AIService(config=config, db=db)

    dp = Dispatcher()
    dp["config"] = config
    dp["db"] = db
    dp["ai_service"] = ai_service

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

    runner: web.AppRunner | None = None
    if start_web:
        try:
            runner = await start_health_server()
        except Exception as exc:
            logger.warning("Health serverni yoqishda xatolik: %s", exc)

    keep_alive_task = asyncio.create_task(render_keep_alive_loop())

    try:
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
                    handle_signals=start_web,
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
    finally:
        keep_alive_task.cancel()
        if runner is not None:
            await runner.cleanup()


async def main() -> None:
    await run_bot(start_web=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
