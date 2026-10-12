import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SYSTEM_PROMPT = (
    "Sen aqlli, xushmuomala va ko'p qirrali AI yordamchisan (ChatGPT kabi). "
    "Foydalanuvchi qaysi tilda yozsa (o'zbek, rus, ingliz va boshqa tillar), "
    "shu tilda ravon, tabiiy, aniq va tushunarli javob ber. "
    "Sening asosiy vazifalaring:\n"
    "1. Savollarga aniq, foydali va mantiqiy javob berish.\n"
    "2. Matn yozish, tahrirlash, qisqartirish va uslubini yaxshilash.\n"
    "3. Matnlarni turli tillar o'rtasida sifatli tarjima qilish.\n"
    "4. Dasturlash kodlarini yozish, tushuntirish va xatolarini (bug) tuzatish.\n"
    "5. Matematika, mantiq va boshqa fanlardan masalalarni qadamma-qadam yechish.\n"
    "6. Kreativ g'oyalar, rejalar va tavsiyalar ishlab chiqish.\n"
    "Javoblaringni o'qishga qulay qilib formatla."
)


@dataclass(frozen=True)
class Config:
    bot_token: str
    openai_api_key: str
    openai_model: str
    openai_base_url: str | None
    max_context_messages: int
    max_context_chars: int
    db_path: str
    system_prompt: str


def load_config() -> Config:
    """Atrof-muhit o'zgaruvchilaridan (.env) sozlamalarni yuklaydi va tekshiradi."""
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    openai_base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None

    if not bot_token or bot_token == "your_telegram_bot_token_here":
        raise ValueError("BOT_TOKEN topilmadi! .env fayliga Telegram bot tokeningizni kiriting.")

    # Agar shaxsiy OPENAI_API_KEY kiritilmagan bo'lsa, OpenAI-mos bepul shlyuz orqali ishlaydi
    if not openai_api_key or openai_api_key == "your_openai_api_key_here":
        openai_api_key = "pollinations-openai-bridge"
        if not openai_base_url:
            openai_base_url = "https://text.pollinations.ai/openai"
        if openai_model == "gpt-4o-mini":
            openai_model = "openai"

    try:
        max_context_messages = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
    except ValueError:
        max_context_messages = 20

    try:
        max_context_chars = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))
    except ValueError:
        max_context_chars = 12000

    db_path = os.getenv("DB_PATH", "data/bot.db").strip() or "data/bot.db"
    system_prompt = os.getenv("SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT).strip() or DEFAULT_SYSTEM_PROMPT

    return Config(
        bot_token=bot_token,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        openai_base_url=openai_base_url,
        max_context_messages=max_context_messages,
        max_context_chars=max_context_chars,
        db_path=db_path,
        system_prompt=system_prompt,
    )
