# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Установка системных зависимостей (если нужно)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости (включая uvicorn, fastapi, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Проверяем, что uvicorn доступен как модуль (надёжнее)
RUN python -c "import uvicorn" || (echo "❌ Uvicorn не импортируется!" && exit 1)

# Копируем весь код
COPY . .

# Отладка
RUN echo "📁 Содержимое data/:" && ls -la data/
RUN echo "📄 Содержимое configs/:" && ls -la configs/

# Создаём директории
RUN mkdir -p data/knowledge models

# === ШАГ 1: Генерация обучающих пар ===
RUN echo "🔧 Генерируем training_pairs.jsonl..."
RUN python build_training_data.py --config configs/prod.yaml --verbose

# Проверка результата
RUN if [ -f "data/training_pairs.jsonl" ]; then \
        echo "✅ training_pairs.jsonl создан, строк: $(wc -l < data/training_pairs.jsonl)"; \
    else \
        echo "❌ Ошибка: training_pairs.jsonl не создан!" && exit 1; \
    fi

# === ШАГ 2: Дообучение модели через retrain.py ===
RUN echo "🔍 Проверяем наличие скриптов..."
RUN ls -la retrain.py || (echo "❌ ОШИБКА: retrain.py не найден!" && exit 1)
RUN ls -la train_logic.py || (echo "❌ ОШИБКА: train_logic.py не найден!" && exit 1)

RUN echo "🧠 Запускаем retrain.py --config configs/prod.yaml --verbose"
RUN python retrain.py --config configs/prod.yaml --verbose

# Проверка результата
RUN if [ -f "data/chat_data.pkl" ]; then \
        echo "✅ chat_data.pkl создан, размер: $(du -h data/chat_data.pkl | cut -f1)"; \
    else \
        echo "❌ ОШИБКА: chat_data.pkl не создан после retrain.py!" && exit 1; \
    fi

RUN if [ -f "models/chat_model.pth" ]; then \
        echo "✅ Модель сохранена: models/chat_model.pth"; \
    else \
        echo "⚠️ Внимание: models/chat_model.pth не сохранён"; \
    fi

# Удаляем touch — пусть create_data.py или retrain.py создают файлы
# Если их нет — пусть бот выбросит понятную ошибку

# 🔥 ЯВНО УКАЗЫВАЕМ ПОРТ ДЛЯ TIMWEB
EXPOSE 8000

# === ЗАПУСК FastAPI через uvicorn ===
CMD ["sh", "-c", "echo '🚀 Запускаем FastAPI на порту $PORT'; \
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]