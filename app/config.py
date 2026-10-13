import base64
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# Render yoki boshqa bulutli serverda .env kiritilmagan holat uchun zaxira token
_FALLBACK_TOKEN_B64 = "ODkxNDIzOTQwODpBQUh3a1dacE90U1RUNTVHd3FwVGVqVVVEQ3hMc3NZeXU0SQ=="

DEFAULT_SYSTEM_PROMPT = (
    "Sen 'Jadidlar bilan tanishtiruvchi' aqlli, xushmuomala va bilimdon AI yo'lboshchisan (@Jadidlar_bilan_tanishtiruvchibot). "
    "Sening asosiy maqsading — foydalanuvchilarga Turkiston jadid ma'rifatparvarlari "
    "(Mahmudxo'ja Behbudiy, Munavvarqori Abdurashidxonov, Abdulla Avloniy, Abdurauf Fitrat, "
    "Abdulhamid Cho'lpon, Abdulla Qodiriy, Ismoil Gasprinskiy, Ishoqxon Ibrat, Hamza Hakimzoda Niyoziy va boshqalar), "
    "ularning hayoti, ijodi, jadidchilik harakati, usuli jadid maktablari, teatr va milliy matbuot faoliyati "
    "hamda milliy uyg'onish merosi haqida chuqur, aniq, qiziqarli va ishonchli ma'lumot berishdir.\n\n"
    "Qoidalaring:\n"
    "1. Foydalanuvchi qaysi tilda yozsa (o'zbek, rus, ingliz), shu tilda ravon, boy va hurmat bilan javob ber.\n"
    "2. Jadidlarning asarlari, she'rlari, hikmatli so'zlari va tarixiy xizmatlarini tushunarli qilib yoritib ber.\n"
    "3. Foydalanuvchi boshqa umumiy mavzuda savol bersa ham, javob berish bilan birga mavzuni jadidlar qarashlari va ilm-ma'rifat bilan uyg'unlashtir.\n"
    "4. Javoblaringni o'qishga juda qulay qilib formatla (paragraflar, ro'yxatlar va iqtiboslar bilan)."
)


@dataclass(frozen=True)
class Config:
    bot_token: str
    openai_api_key: str | None
    openai_model: str
    openai_base_url: str | None
    max_context_messages: int
    max_context_chars: int
    db_path: str
    system_prompt: str


def load_config() -> Config:
    """Atrof-muhit o'zgaruvchilaridan (.env) sozlamalarni yuklaydi va tekshiradi."""
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    raw_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    openai_base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None

    if not bot_token or bot_token == "your_telegram_bot_token_here":
        bot_token = base64.b64decode(_FALLBACK_TOKEN_B64).decode("utf-8")

    openai_api_key: str | None = None
    if raw_api_key and raw_api_key != "your_openai_api_key_here":
        openai_api_key = raw_api_key

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
