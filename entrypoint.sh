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

# === ЗАГРУЗКА Qwen2.5-3B (публичная модель, без токенов) ===
if [ ! -d "/app/models/qwen2.5-3b" ] || [ -z "$(ls -A /app/models/qwen2.5-3b 2>/dev/null)" ]; then
    echo "📥 Загрузка Qwen2.5-3B-Instruct из HuggingFace (публичная модель)..."
    echo "   Модель: Qwen/Qwen2.5-3B-Instruct"
    echo "   Сохранение: /app/models/qwen2.5-3b/"
    echo "   Размер: ~6 ГБ (5-15 минут)"
    python -c "
import os
import sys
from huggingface_hub import snapshot_download

model_id = 'Qwen/Qwen2.5-3B-Instruct'
local_dir = '/app/models/qwen2.5-3b'

try:
    snapshot_download(
        repo_id=model_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,
    )
    print(f'✅ Модель {model_id} загружена в {local_dir}')
except Exception as e:
    print(f'⚠️ Не удалось загрузить модель: {e}')
    print('ℹ️ Бот будет использовать fallback-модель при запуске')
    sys.exit(0)  # Не блокируем запуск
" 2>&1 || echo "⚠️ Fallback: загрузка модели не удалась, бот запустится с базовой моделью"
else
    echo "✅ Qwen2.5-3B уже загружена в /app/models/qwen2.5-3b"
fi

# === ЗАПУСК UVICORN ===
echo "✅ Запускаю uvicorn на ${HOST:-0.0.0.0}:${PORT:-8000}..."
exec uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}
