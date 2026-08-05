#!/bin/bash
set -e

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

# === ЗАГРУЗКА МОДЕЛИ ИЗ HUGGINGFACE (только при первом запуске) ===
if [ ! -d "/app/models/rugpt3" ] || [ -z "$(ls -A /app/models/rugpt3 2>/dev/null)" ]; then
    echo "📥 Загрузка модели Pantikur/Wuglarst из HuggingFace..."
    python -c "
import os
import sys
from huggingface_hub import snapshot_download

model_id = 'Pantikur/Wuglarst'
local_dir = '/app/models/rugpt3'

try:
    snapshot_download(
        repo_id=model_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
        timeout=300
    )
    print(f'✅ Модель {model_id} загружена в {local_dir}')
except Exception as e:
    print(f'⚠️ Не удалось загрузить модель: {e}')
    print('ℹ️ Бот будет использовать fallback-модель при запуске')
    sys.exit(0)  # Не блокируем запуск
" 2>&1 || echo "⚠️ Fallback: загрузка модели не удалась, бот запустится с базовой моделью"
else
    echo "✅ Модель уже загружена в /app/models/rugpt3"
fi

# === ЗАПУСК UVICORN ===
echo "✅ Запускаю uvicorn на ${HOST:-0.0.0.0}:${PORT:-8000}..."
exec uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
