@echo off
echo Telegram AI Chatbot fonda to'xtatilmoqda...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -match 'python|cmd') -and ($_.CommandLine -match 'main\.py|run_24_7\.bat') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
echo Bot to'xtatildi.
