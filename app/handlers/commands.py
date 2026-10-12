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
        "Men 24/7 ishlaydigan <b>AI suhbatdosh va yordamchi botman</b> (ChatGPT kabi).\n\n"
        "✨ <b>Imkoniyatlarim:</b>\n"
        "• 💬 Istalgan mavzuda tabiiy suhbatlashish\n"
        "• ✍️ Maqola, post, insho va matnlar yozish hamda tahrirlash\n"
        "• 🌐 O'zbek, rus, ingliz va boshqa tillarda erkin muloqot hamda tarjima\n"
        "• 💻 Dasturlash kodlarini yozish va xatolarni topish\n"
        "• 🧮 Matematika va mantiqiy masalalarni yechish\n"
        "• 💡 Yangi g'oyalar va rejalar ishlab chiqish\n\n"
        "📌 <b>Foydali buyruqlar:</b>\n"
        "/clear — Suhbat tarixini tozalash (yangi mavzu boshlash)\n"
        "/help — Yordam va qo'llanma\n"
        "/about — Bot haqida ma'lumot\n\n"
        "👇 <i>Menga savolingizni yoki topshirig'ingizni oddiy xabar sifatida yozib yuboring!</i>"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """/help buyrug'i: botdan foydalanish bo'yicha yordam."""
    help_text = (
        "📖 <b>Yordam va foydalanish qo'llanmasi</b>\n\n"
        "Bot bilan xuddi oddiy suhbatdosh yoki ChatGPT bilan gaplashgandek muloqot qilishingiz mumkin:\n\n"
        "1️⃣ <b>Savol bering:</b> Istalgan tilda savol yoki topshiriq yuboring.\n"
        "2️⃣ <b>Kontekstni davom ettiring:</b> Bot oldingi xabarlaringizni eslab qoladi, "
        "shuning uchun suhbatni bemalol davom ettirishingiz mumkin.\n"
        "3️⃣ <b>Yangi mavzu:</b> Agar suhbat mavzusini butunlay o'zgartirmoqchi bo'lsangiz, "
        "/clear buyrug'ini bering.\n\n"
        "🛠 <b>Mavjud buyruqlar:</b>\n"
        "• /start — Botni qayta ishga tushirish\n"
        "• /help — Ushbu yordam oynasini ko'rsatish\n"
        "• /clear — Joriy suhbat tarixini tozalash\n"
        "• /about — Bot va texnologiyalar haqida ma'lumot"
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
            "ℹ️ Suhbat tarixingiz allaqachon bo'sh. Menga istalgan savolingizni yozishingiz mumkin!",
            parse_mode=ParseMode.HTML,
        )


@router.message(Command("about"))
async def cmd_about(message: Message, config: Config) -> None:
    """/about buyrug'i: bot haqida ma'lumot."""
    about_text = (
        "🤖 <b>Telegram AI Chatbot — 24/7</b>\n\n"
        "Ushbu bot sun'iy intellekt (OpenAI) yordamida foydalanuvchilarga "
        "kun-u tun (24/7) tezkor va aqlli yordam berish uchun yaratilgan.\n\n"
        "⚙️ <b>Texnik xususiyatlar:</b>\n"
        f"• <b>AI Model:</b> <code>{config.openai_model}</code>\n"
        "• <b>Platforma:</b> Python 3.12+ va aiogram 3.x\n"
        "• <b>Xotira:</b> Har bir foydalanuvchi uchun alohida SQLite suhbat konteksti\n"
        "• <b>Tillar:</b> O'zbek, Rus, Ingliz va boshqa tillar\n\n"
        "💡 Suhbat tarixini yangilash uchun /clear buyrug'idan foydalaning."
    )
    await message.answer(about_text, parse_mode=ParseMode.HTML)
