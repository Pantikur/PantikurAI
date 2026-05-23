# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Проверяем uvicorn
RUN python -c "import uvicorn" || (echo "❌ Uvicorn не импортируется!" && exit 1)

# Копируем код приложения
COPY . .

# Создаём директории
RUN mkdir -p data models

# ⚠️ Проверяем наличие модели (но НЕ обучаем!)
RUN if [ ! -f "models/chat_model.pth" ]; then \
        echo "🚨 ОШИБКА: models/chat_model.pth отсутствует! Обучите модель локально и добавьте в образ или смонтируйте volume."; \
        exit 1; \
    else \
        echo "✅ Модель найдена"; \
    fi

RUN if [ ! -f "data/chat_data.pkl" ]; then \
        echo "🚨 ОШИБКА: data/chat_data.pkl отсутствует!"; \
        exit 1; \
    else \
        echo "✅ Токенизатор найден"; \
    fi

EXPOSE 8000

# Запуск API
CMD ["sh", "-c", "echo '🚀 Запускаем FastAPI на порту $PORT'; \
    exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]