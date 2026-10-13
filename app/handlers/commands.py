from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from app.config import Config
from app.database import Database

router = Router(name="commands")


@router.message(CommandStart())
async def cmd_start(message: Message, db: Database) -> None:
    """/start buyrug'i: foydalanuvchini ro'yxatdan o'tkazish va salomlashish."""
    user = message.from_user
    if user:
        await db.upsert_user(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            language_code=user.language_code,
        )
        first_name = user.first_name or "do'stim"
    else:
        first_name = "do'stim"

    welcome_text = (
        f"👋 Assalomu alaykum, <b>{first_name}</b>!\n\n"
        "Xush kelibsiz! Men <b>Jadidlar bilan tanishtiruvchi AI botman</b> (@Jadidlar_bilan_tanishtiruvchibot).\n\n"
        "📚 <b>Men orqali bilib olishingiz mumkin:</b>\n"
        "• 📜 Turkiston jadidlari (Behbudiy, Avloniy, Fitrat, Cho'lpon, Qodiriy va b.) hayoti va merosi\n"
        "• 📖 Jadidlarning nodir asarlari, romanlari, she'rlari va maqolalari\n"
        "• 🏫 Yangi usul (usuli jadid) maktablari, teatr va milliy matbuot tarixi\n"
        "• 💡 Ularning ilm-ma'rifat va milliy ozodlik haqidagi ibratli fikrlari\n\n"
        "📌 <b>Foydali buyruqlar:</b>\n"
        "/clear — Suhbat tarixini tozalash (yangi mavzu boshlash)\n"
        "/help — Yordam va savol namunalari\n"
        "/about — Bot haqida ma'lumot\n\n"
        "👇 <i>Istalgan savolingizni yozing: masalan, 'Mahmudxo\\'ja Behbudiy kim bo\\'lgan?' yoki 'Jadidlar qanday gazetalarni chiqargan?'</i>"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """/help buyrug'i: botdan foydalanish bo'yicha yordam."""
    help_text = (
        "📖 <b>Botdan foydalanish bo'yicha qo'llanma</b>\n\n"
        "Menga jadidlar hayoti, asarlari va o'sha davr tarixi haqida istalgan shaklda savol berishingiz mumkin.\n\n"
        "💡 <b>Savol namunalari:</b>\n"
        "• <i>\"Jadidchilik harakati qachon va qanday boshlangan?\"</i>\n"
        "• <i>\"Abdulla Qodiriyning 'O'tkan kunlar' romani haqida ma'lumot ber\"</i>\n"
        "• <i>\"Abdulhamid Cho'lponning eng mashhur she'rlari qaysilar?\"</i>\n"
        "• <i>\"Munavvarqori Abdurashidxonov qanday maktablar ochgan?\"</i>\n\n"
        "🛠 <b>Mavjud buyruqlar:</b>\n"
        "• /start — Botni qayta ishga tushirish\n"
        "• /help — Ushbu yordam menyusi\n"
        "• /clear — Joriy suhbat tarixini tozalash\n"
        "• /about — Bot haqida batafsil ma'lumot"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


@router.message(Command("clear"))
async def cmd_clear(message: Message, db: Database) -> None:
    """/clear buyrug'i: foydalanuvchining joriy suhbat tarixini tozalaydi."""
    if not message.from_user:
        return

    deleted_count = await db.clear_user_history(message.from_user.id)
    if deleted_count > 0:
        await message.answer(
            "🧹 <b>Suhbat tarixi tozalandi!</b>\n"
            "Endi yangi mavzuda suhbatni boshlashingiz mumkin.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            "ℹ️ Suhbat tarixingiz allaqachon bo'sh. Menga jadidlar haqida istalgan savolingizni berishingiz mumkin!",
            parse_mode=ParseMode.HTML,
        )


@router.message(Command("about"))
async def cmd_about(message: Message, config: Config) -> None:
    """/about buyrug'i: bot haqida ma'lumot."""
    about_text = (
        "📚 <b>Jadidlar bilan tanishtiruvchi bot</b> (@Jadidlar_bilan_tanishtiruvchibot)\n\n"
        "Ushbu bot milliy uyg'onish va ma'rifatparvarlik yetakchilari — jadid bobolarimizning "
        "bebaho merosini yoshlar va barcha qiziquvchilarga sun'iy intellekt orqali interaktiv "
        "ravishda tanishtirish maqsadida yaratilgan.\n\n"
        "⚙️ <b>Texnik xususiyatlar:</b>\n"
        f"• <b>AI Model:</b> <code>{config.openai_model}</code>\n"
        "• <b>Platforma:</b> Python 3.12+, Aiogram 3.x\n"
        "• <b>Ishlash tartibi:</b> 24/7 uzluksiz rejim va xotira konteksti\n\n"
        "💡 Suhbat tarixini yangilash uchun /clear buyrug'idan foydalaning."
    )
    await message.answer(about_text, parse_mode=ParseMode.HTML)
