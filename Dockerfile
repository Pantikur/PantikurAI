# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Установка системных зависимостей — ДОБАВИЛ curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    echo '✅ Все зависимости установлены'

# Проверяем Uvicorn
RUN python -c "import uvicorn" && \
    echo '✅ Uvicorn импортирован успешно' || \
    (echo '❌ Ошибка: uvicorn не установлен!' && exit 1)

# Копируем код приложения
COPY . .

# Создаём необходимые директории
RUN mkdir -p models data

# Экспортируем переменные окружения по умолчанию
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Запуск: проверяем данные и модель, при необходимости скачиваем с Google Drive
CMD ["sh", "-c", " \
    echo '📁 Проверяем наличие данных...'; \
    if [ ! -f 'data/chat_data.pkl' ] && [ ! -f 'data/training_pairs.jsonl' ]; then \
        echo '🚨 Нет данных для обучения! Добавьте chat_data.pkl или training_pairs.jsonl в папку data'; \
        exit 1; \
    fi; \
    \
    if [ ! -f 'models/chat_model.pth' ]; then \
        echo '📥 Модель не найдена. Скачиваю с Google Drive...'; \
        curl -# -L 'https://drive.google.com/uc?export=download&id=1POLpxWHyN4_dYb3Sl1IUZuK01kbp3-1i' -o models/chat_model.pth || \
        (echo '❌ Не удалось скачать модель!' && exit 1); \
    else \
        echo '✅ Используем существующую модель: models/chat_model.pth'; \
    fi; \
    \
    if [ ! -f 'data/chat_data.pkl' ] && [ -f 'data/training_pairs.jsonl' ]; then \
        echo '🔄 Конвертируем training_pairs.jsonl в chat_data.pkl...'; \
        python convert_data.py || (echo '❌ Ошибка конвертации данных!' && exit 1); \
    fi; \
    \
    echo '🚀 Запускаем FastAPI на порту $PORT'; \
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 \
"]