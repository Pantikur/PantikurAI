# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Проверяем Uvicorn
RUN python -c "import uvicorn" || (echo "❌ Ошибка: uvicorn не установлен!" && exit 1)

# Копируем код приложения
COPY . .

# Создаём необходимые директории
RUN mkdir -p models data

# Экспортируем переменные окружения по умолчанию
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Запуск: проверяем данные и модель, при необходимости обучаем
CMD ["sh", "-c", " \
    echo '📁 Проверяем наличие данных...'; \
    if [ ! -f 'data/chat_data.pkl' ] && [ ! -f 'data/training_pairs.jsonl' ]; then \
        echo '🚨 Нет данных для обучения! Добавьте chat_data.pkl или training_pairs.jsonl в папку data'; \
        exit 1; \
    fi; \
    \
    if [ ! -f 'models/chat_model.pth' ]; then \
        echo '⚠️ Модель не найдена. Запускаю обучение...'; \
        python train.py || (echo '❌ Обучение не удалось!' && exit 1); \
    else \
        echo '✅ Используем существующую модель: models/chat_model.pth'; \
    fi; \
    \
    echo '🚀 Запускаем FastAPI на порту $PORT'; \
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 \
"]