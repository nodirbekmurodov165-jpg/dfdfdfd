@echo off
echo Telegram AI Chatbot fonda to'xtatilmoqda...
schtasks /Delete /TN "TelegramAIBot24x7" /F >nul 2>&1
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -match 'python|cmd') -and ($_.CommandLine -match 'main\.py|run_24_7\.bat') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
echo Bot to'xtatildi. Qayta yoqish uchun start_24_7_background.vbs faylini ishga tushiring.
