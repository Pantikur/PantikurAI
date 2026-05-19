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

# === ОТЛАДКА: проверяем структуру ===
RUN echo "=== Содержимое /app ===" && ls -la
RUN echo "=== Содержимое Wuglarst/src ===" && ls -la Wuglarst/src || true

# Создаём нужные директории
RUN mkdir -p data models

# === ГЕНЕРАЦИЯ chat_data.pkl и модели (опционально) ===
# Если есть retrain.py — попробуем обучить модель
# Если нет — создаём пустые файлы, чтобы не упало при старте

# Проверяем наличие retrain.py или train.py
RUN if [ -f "retrain.py" ]; then \
        echo "🔄 Запускаем дообучение при сборке..."; \
        python retrain.py || echo "⚠️ Дообучение не удалось — возможно, нет данных"; \
    elif [ -f "train.py" ]; then \
        echo "🔄 Запускаем обучение через train.py..."; \
        python train.py || echo "⚠️ Обучение не удалось"; \
    else \
        echo "⚠️ Нет ни retrain.py, ни train.py — пропускаем обучение"; \
    fi

# Гарантируем, что файлы существуют
RUN touch data/chat_data.pkl models/chat_model.pth

# 🔥 ЯВНО УКАЗЫВАЕМ ПОРТ ДЛЯ TIMWEB
EXPOSE 8000

# === ЗАПУСК FastAPI через uvicorn ===
CMD ["sh", "-c", "echo '🚀 Запускаем FastAPI на порту $PORT'; \
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]