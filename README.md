# 📚 Jadidlar bilan tanishtiruvchi AI Bot (@Jadidlar_bilan_tanishtiruvchibot)

Turkiston jadid ma'rifatparvarlari (Behbudiy, Avloniy, Fitrat, Cho'lpon, Qodiriy va b.) hayoti, ijodi, asarlari va milliy uyg'onish merosini sun'iy intellekt orqali 24/7 rejimda tanishtiruvchi Telegram AI bot.

## ✨ Asosiy imkoniyatlar
- 📜 **Jadidlar ensiklopediyasi**: Jadidchilik harakati, usuli jadid maktablari, teatr va matbuot haqida batafsil ma'lumotlar.
- 💬 **Tabiiy va boy muloqot**: O‘zbek, rus, ingliz va boshqa tillarda erkin va hurmat bilan suhbatlashish.
- 🧠 **Kontekst xotirasi**: Har bir foydalanuvchining suhbat tarixi SQLite bazasida alohida saqlanadi.
- 📏 **Aqlli xabar boshqaruvi**: Telegram cheklovlariga mos uzun matnlarni bo'lib yuborish.
- 🛡 **Barqaror 24/7 ishlash**: Asinxron arxitektura (`aiogram 3.x` + `aiosqlite`), avtomatik qayta ulanish va fonda mustaqil ishlash.

---

## 📁 Loyiha tuzilmasi
```text
bot/
├── app/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── commands.py       # /start, /help, /clear, /about buyruqlari
│   │   └── chat.py           # Matnli xabarlar va AI muloqoti
│   ├── services/
│   │   └── ai_service.py     # OpenAI API integratsiyasi va xatolarni boshqarish
│   ├── utils/
│   │   └── text_splitter.py  # Uzun xabarlarni bo'laklash (4096 belgi limiti)
│   ├── config.py             # .env konfiguratsiya yuklagich
│   └── database.py           # SQLite asinxron baza boshqaruvchisi
├── .env.example              # Maxfiy kalitlar namunasi
├── Dockerfile                # Docker imiji
├── docker-compose.yml        # 24/7 Docker Compose sozlamasi
├── main.py                   # Asosiy ishga tushirish fayli
└── requirements.txt          # Kerakli Python kutubxonalar
```

---

## 🚀 O‘rnatish va ishga tushirish

### 1. Virtual muhit yaratish va kutubxonalarni o‘rnatish
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. `.env` faylini sozlash
`.env.example` faylidan `.env` nomi bilan nusxa oling va kalitlaringizni kiriting:
```powershell
Copy-Item .env.example .env
```
`.env` ichiga:
- `BOT_TOKEN` — `@BotFather` dan olingan Telegram bot tokeni
- `OPENAI_API_KEY` — OpenAI API kalitingiz

### 3. Botni ishga tushirish
```powershell
python main.py
```

---

## 🐳 24/7 Docker orqali ishga tushirish (Server uchun)
```bash
docker compose up -d --build
```
`restart: always` sozlamasi tufayli bot server qayta yonganida yoki xatolik yuz berganda avtomatik ravishda 24/7 rejimda qayta ishga tushadi.
