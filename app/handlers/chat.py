from aiogram import F, Router
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from app.database import Database
from app.services.ai_service import AIService
from app.utils.text_splitter import send_chunked_message

router = Router(name="chat")


@router.message(F.text)
async def handle_text_message(
    message: Message,
    db: Database,
    ai_service: AIService,
) -> None:
    """Foydalanuvchidan kelgan matnli xabarlarni qabul qilib, AI javobini qaytaradi."""
    user = message.from_user
    if not user or not message.text:
        return

    user_text = message.text.strip()
    if not user_text:
        return

    # Foydalanuvchi ma'lumotlari va oxirgi faollik vaqtini yangilaymiz
    await db.upsert_user(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        language_code=user.language_code,
    )

    # AI javob berguncha "typing..." holatini ko'rsatib turamiz
    async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):  # type: ignore[arg-type]
        reply_text = await ai_service.generate_reply(user_id=user.id, user_text=user_text)

    # Telegram uzunlik cheklovini hisobga olgan holda javobni yuboramiz
    await send_chunked_message(message, reply_text)


@router.message()
async def handle_non_text_message(message: Message) -> None:
    """Matndan boshqa turdagi xabarlar uchun tushunarli javob."""
    await message.answer(
        "📝 Iltimos, menga matn ko'rinishida xabar yuboring. "
        "Men hozircha faqat matnli xabarlar bilan ishlay olaman."
    )
