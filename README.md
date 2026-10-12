# 🤖 Telegram AI Chatbot — 24/7

ChatGPT kabi tabiiy muloqot qiluvchi, har bir foydalanuvchi uchun suhbat kontekstini eslab qoluvchi va 24/7 ishlashga mo‘ljallangan Telegram AI bot.

## ✨ Asosiy imkoniyatlar
- 💬 **Tabiiy suhbat**: O‘zbek, rus, ingliz va boshqa tillarda erkin muloqot.
- 🧠 **Kontekst xotirasi**: Har bir foydalanuvchining suhbat tarixi SQLite bazasida alohida saqlanadi.
- 📏 **Aqlli cheklov boshqaruvi**: Juda uzun suhbatlarda kontekst hajmini avtomatik boshqaradi va Telegramning 4096 belgilik chekloviga mos ravishda uzun javoblarni mantiqiy bo‘laklarga bo‘lib yuboradi.
- 🛠 **Ko‘p qirrali yordamchi**: Matn yozish, tahrirlash, tarjima qilish, dasturlash kodlari yozish, masalalar yechish va g‘oyalar berish.
- 🛡 **Barqaror 24/7 ishlash**: Asinxron arxitektura (`aiogram 3.x` + `aiosqlite` + `AsyncOpenAI`), xatolarni ushlash va `logs/bot.log` ga yozib borish.

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
