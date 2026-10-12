import logging
from pathlib import Path
import aiosqlite

logger = logging.getLogger(__name__)


class Database:
    """SQLite ma'lumotlar bazasi bilan asinxron ishlash klassi."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init_db(self) -> None:
        """Jadvallarni va indekslarni yaratadi."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA journal_mode=WAL;")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    full_name TEXT,
                    language_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_messages_user_id
                ON messages (user_id, id DESC)
                """
            )
            await db.commit()
        logger.info("SQLite ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi: %s", self.db_path)

    async def upsert_user(
        self,
        user_id: int,
        username: str | None,
        full_name: str,
        language_code: str | None = None,
    ) -> None:
        """Foydalanuvchi ma'lumotlarini qo'shadi yoki yangilaydi."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, username, full_name, language_code, last_active)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name,
                    language_code = excluded.language_code,
                    last_active = CURRENT_TIMESTAMP
                """,
                (user_id, username, full_name, language_code),
            )
            await db.commit()

    async def add_message(
        self,
        user_id: int,
        role: str,
        content: str,
        keep_limit: int = 100,
    ) -> None:
        """
        Yangi xabarni saqlaydi va baza hajmi haddan tashqari oshib ketmasligi uchun
        har bir foydalanuvchining eng oxirgi `keep_limit` ta xabarini saqlab qoladi.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
                (user_id, role, content),
            )
            await db.execute(
                """
                DELETE FROM messages
                WHERE user_id = ?
                  AND id NOT IN (
                      SELECT id FROM messages
                      WHERE user_id = ?
                      ORDER BY id DESC
                      LIMIT ?
                  )
                """,
                (user_id, user_id, keep_limit),
            )
            await db.commit()

    async def get_context_messages(
        self,
        user_id: int,
        max_messages: int = 20,
        max_chars: int = 12000,
    ) -> list[dict[str, str]]:
        """
        Foydalanuvchining oxirgi xabarlarini kontekst uchun qaytaradi.
        Uzun suhbatlarda ham xabarlar soni (`max_messages`), ham belgilar hajmi (`max_chars`)
        bo'yicha kontekstni avtomatik boshqaradi.
        """
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT role, content
                FROM messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, max_messages),
            )
            rows = await cursor.fetchall()

        # Eng yangi xabarlardan boshlab hajmni hisoblaymiz
        selected_reversed: list[dict[str, str]] = []
        total_chars = 0

        for row in rows:
            role = row["role"]
            content = row["content"]
            msg_len = len(content)

            if selected_reversed and (total_chars + msg_len > max_chars):
                break

            selected_reversed.append({"role": role, "content": content})
            total_chars += msg_len

        # Xronologik tartibga qaytaramiz (eskidan yangiga)
        selected_reversed.reverse()
        return selected_reversed

    async def clear_user_history(self, user_id: int) -> int:
        """Foydalanuvchining suhbat tarixini tozalaydi va o'chirilgan xabarlar sonini qaytaradi."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM messages WHERE user_id = ?",
                (user_id,),
            )
            deleted_count = cursor.rowcount
            await db.commit()
            return deleted_count or 0
