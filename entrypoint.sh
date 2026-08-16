#!/bin/bash
set -e

echo "🚀 Запуск Pantikur ChatBot..."

# === СОЗДАЁМ RUNTIME-ДИРЕКТОРИИ ===
echo "📁 Инициализация runtime-директорий..."
mkdir -p /app/logs
mkdir -p /app/akva/data/communication
mkdir -p /app/akva/data/reports
mkdir -p /app/akva/akva/engine/state
mkdir -p /app/ayiko/ojidania
mkdir -p /app/ayiko/aiko_foto
mkdir -p /app/fuyuki/data
mkdir -p /app/fuyuki/models
mkdir -p /app/fuyuki/engine/state
mkdir -p /app/data
mkdir -p /app/shiori/polygon

# === ПРОВЕРКА НАЛИЧИЯ КРИТИЧНЫХ ФАЙЛОВ (fail-fast) ===
echo "🔍 Проверка критичных файлов..."
MISSING=0
for f in main.py barston_lore_loader.py utils/human_params.py; do
    if [ -f "/app/$f" ]; then
        echo "   ✅ $f"
    else
        echo "   ❌ $f ОТСУТСТВУЕТ!"
        MISSING=1
    fi
done
if [ "$MISSING" -eq 1 ]; then
    echo "❌ Критичные файлы отсутствуют — контейнер не может запуститься!"
    exit 1
fi

# === ПРОВЕРКА ЗАВИСИМОСТЕЙ ===
echo "📦 Проверка зависимостей..."
python -c "import fastapi; import uvicorn; import transformers; print('✅ Зависимости OK')"

# === ЗАПУСК UVICORN ===
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
echo "✅ Запускаю uvicorn на ${HOST}:${PORT}..."
echo "   PYTHONPATH=$PYTHONPATH"

# exec заменяет процесс — контейнер живёт пока жив uvicorn
exec uvicorn main:app \
    --host ${HOST} \
    --port ${PORT} \
    --log-level info \
    --workers 1