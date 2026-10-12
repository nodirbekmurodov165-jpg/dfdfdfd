"""
Telegram AI Chatbot ilova paketi.
Agar Render.com da Start Command sifatida standart `gunicorn app:app` qolib ketgan bo'lsa ham,
ushbu fayl botni fon oqimida (background thread) avtomatik ishga tushiradi va HTTP 200 qaytaradi.
"""
import asyncio
import threading
from typing import Callable, Iterable

_bot_thread_started = False
_lock = threading.Lock()


def _start_bot_in_background() -> None:
    global _bot_thread_started
    with _lock:
        if _bot_thread_started:
            return
        _bot_thread_started = True

        def _runner() -> None:
            from main import run_bot
            asyncio.run(run_bot(start_web=False))

        thread = threading.Thread(target=_runner, daemon=True, name="TelegramBotThread")
        thread.start()


def app(environ: dict, start_response: Callable) -> Iterable[bytes]:
    """WSGI ilovasi (`gunicorn app:app` uchun)."""
    _start_bot_in_background()
    status = "200 OK"
    body = b"Telegram AI Chatbot 24/7 is running!"
    headers = [
        ("Content-Type", "text/plain; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]


# Gunicorn modulni import qilgan zahoti botni ishga tushiramiz
if "gunicorn" in (__import__("sys").modules.keys()):
    _start_bot_in_background()
