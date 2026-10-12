@echo off
cd /d "%~dp0"
title Telegram AI Chatbot - 24/7 Watchdog

:loop
echo [%date% %time%] Telegram AI Chatbot ishga tushirilmoqda...
python main.py
echo [%date% %time%] Bot to'xtadi. 5 soniyadan so'ng qayta ishga tushiriladi...
timeout /t 5 /nobreak >nul
goto loop
