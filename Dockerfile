# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .

# Установка зависимостей с PyTorch (CPU)
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt && \
    echo '✅ Все зависимости установлены'

# Копируем код приложения
COPY . .

# Создаём необходимые директории
RUN mkdir -p models data logs

# Экспортируем переменные окружения
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTORCH_ENABLE_MPS_FALLBACK=1

# === Проверка входной точки ===
RUN python -c "from main import app" && \
    echo '✅ Приложение импортировано успешно'

# === Рекомендуемый способ: gunicorn + uvicorn workers ===
# Это обеспечит стабильную работу с несколькими процессами
RUN pip install --no-cache-dir gunicorn uvicorn[standard]

# Открываем порт (для документации и хостинга)
EXPOSE $PORT

# Запуск через gunicorn с uvicorn workers
# Автоматически использует PORT из окружения
ENTRYPOINT ["sh", "-c", "gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:\$PORT --timeout 120 --keep-alive 5 --preload"]
# === HEALTHCHECK для Docker ===
# Проверяет, отвечает ли приложение, с задержкой
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1