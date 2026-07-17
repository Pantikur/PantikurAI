@echo off
REM Wuglarst Autonomous Server — Автозапуск
REM Запускает сервер в фоновом режиме

echo ========================================
echo   Wuglarst Autonomous Server
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python не найден!
    echo Установите Python 3.11+
    pause
    exit /b 1
)

echo [1/3] Проверка зависимостей...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Установка fastapi...
    pip install fastapi uvicorn pydantic >nul 2>&1
)

echo [2/3] Проверка сервера...
if not exist "server_autonomous.py" (
    echo ERROR: server_autonomous.py не найден!
    pause
    exit /b 1
)

echo [3/3] Запуск сервера...
echo.

REM Создание директорий
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Запуск в фоне
start /B python server_autonomous.py

echo.
echo ========================================
echo   ✅ Wuglarst запущен!
echo   📡 http://localhost:8001
echo   🏥 http://localhost:8001/health
echo ========================================
echo.
echo Для остановки:
echo   python daemon.py stop
echo.
echo Для установки автозапуска:
echo   python daemon.py install
echo.
pause
