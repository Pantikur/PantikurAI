@echo off
chcp 65001 >nul
echo ========================================
echo   Wuglarst Server - Запуск
echo ========================================
echo.

cd /d "%~dp0wuglarst"

echo Запуск сервера...
echo.
echo Открой браузер и перейди:
echo   http://localhost:8001
echo.
echo Чтобы остановить, нажми Ctrl+C
echo ========================================
echo.

uvicorn server:app --host 0.0.0.0 --port 8001 --reload

pause
