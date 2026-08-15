#!/bin/bash
# set -e  # Убран: Timeweb может не поддерживать exit на некоторых командах

echo "🚀 Запуск Pantikur ChatBot..."

# === СОЗДАЁМ RUNTIME-ДІРЕКТОРИИ (если смонтированы через volumes) ===
echo "📁 Инициализация runtime-директорий..."
mkdir -p /app/akva/data/communication
mkdir -p /app/akva/data/reports
mkdir -p /app/akva/akva/engine/state
mkdir -p /app/ayiko/ojidania
mkdir -p /app/ayiko/aiko_foto
mkdir -p /app/fuyuki/data
mkdir -p /app/fuyuki/models
mkdir -p /app/fuyuki/engine/state
mkdir -p /app/logs
mkdir -p /app/data
mkdir -p /app/shiori/polygon

# === ЗАГРУЗКА Qwen2.5-3B (публичная модель, без токенов) ===
# Загружаем модель В ФОНЕ, не блокируя запуск uvicorn
if [ ! -d "/app/models/qwen2.5-3b" ] || [ -z "$(ls -A /app/models/qwen2.5-3b 2>/dev/null)" ]; then
    echo "⚠️ Папка /app/models/qwen2.5-3b пуста или отсутствует"
    echo "ℹ️ Убедитесь, что модель смонтирована через volumes или уже загружена"
    echo "ℹ️ QwenBot в main.py будет искать модель локально и фоллбэкиться на кэш transformers"
else
    echo "✅ Qwen2.5-3B уже загружена в /app/models/qwen2.5-3b"
fi

# === УСТАНОВКА GOOGLE CHROME (совместимая версия для Selenium) ===
echo "🔧 Установка Google Chrome для Selenium..."
CHROME_BIN_PATH=$(which google-chrome 2>/dev/null || which chromium-browser 2>/dev/null || echo "")
if [ -z "$CHROME_BIN_PATH" ]; then
    echo "📥 Chrome не найден — устанавливаем Google Chrome Stable..."
    CHROME_DEB="/tmp/google-chrome-stable_current_amd64.deb"
    wget -q -O "$CHROME_DEB" https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    if [ -f "$CHROME_DEB" ]; then
        apt-get update -qq && apt-get install -y -qq "$CHROME_DEB" > /dev/null 2>&1
        rm -f "$CHROME_DEB"
        echo "✅ Google Chrome установлен"
    else
        echo "⚠️ Не удалось скачать Google Chrome, пробуем Chromium..."
        apt-get install -y -qq chromium-browser > /dev/null 2>&1 || true
    fi
else
    echo "✅ Chrome уже установлен: $CHROME_BIN_PATH"
fi

# === ПРОВЕРКА ЗАВИСИМОСТЕЙ ===
echo "📦 Проверка зависимостей..."
python -c "import fastapi; import uvicorn; print('✅ Зависимости OK')" || {
    echo "❌ Ошибка: отсутствуют необходимые зависимости!"
    echo "Убедитесь, что requirements.txt установлен корректно"
    exit 1
}

# === ПРОВЕРКА Готовности main.py ===
echo "🔍 Проверка main.py..."
python -c "
import sys
sys.path.insert(0, '/app')
try:
    import main
    print('✅ main.py импортируется успешно')
    print(f'✅ FastAPI app найден: {hasattr(main, \"app\")}')
except Exception as e:
    print(f'⚠️ Ошибка импорта main.py: {e}')
    print('ℹ️ Uvicorn попробует запуститься, но могут быть ошибки')
" 2>&1

# === ЗАПУСК UVICORN ===
echo "✅ Запускаю uvicorn на ${HOST:-0.0.0.0}:${PORT:-8000}..."
echo "📋 Переменные окружения:"
echo "   HOST=${HOST:-0.0.0.0}"
echo "   PORT=${PORT:-8000}"
echo "   PYTHONPATH=${PYTHONPATH}"

# Запускаем uvicorn с правильными параметрами
exec uvicorn main:app \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-8000} \
    --log-level info \
    --workers 1
