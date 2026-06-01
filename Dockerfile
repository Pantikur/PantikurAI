# Используем официальный образ Python 3.10 (или 3.11 — по твоему выбору)
FROM python:3.11-slim

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

# Установка PyTorch (CPU) + остальные пакеты
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt && \
    pip install --no-cache-dir uvicorn gunicorn && \
    echo '✅ Все зависимости установлены'

# Копируем код приложения
COPY . .

# Создаём необходимые директории
RUN mkdir -p models data logs

# Экспорт переменных окружения
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTORCH_ENABLE_MPS_FALLBACK=1

# Проверка, что приложение импортируется
RUN python -c "from main import app" && \
    echo '✅ Приложение импортировано успешно'

# Открываем порт
EXPOSE $PORT

# === HEALTHCHECK — проверяет готовность сервиса ===
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# === ENTRYPOINT (на всякий случай, но НЕ ДОВЕРЯЙ ЕМУ НА PaaS) ===
ENTRYPOINT ["sh", "-c", "exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5"]