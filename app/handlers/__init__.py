from aiogram import Router
from app.handlers.commands import router as commands_router
from app.handlers.chat import router as chat_router


def setup_routers() -> Router:
    """Barcha routerlarni birlashtiradi."""
    main_router = Router()
    main_router.include_router(commands_router)
    main_router.include_router(chat_router)
    return main_router
