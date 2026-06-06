# === БАЗОВЫЙ ОБРАЗ ===
FROM python:3.11-slim

# === СИСТЕМНЫЕ ЗАВИСИМОСТИ (включая curl!) ===
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        curl \
        ca-certificates \
        libev-dev \
        libevent-dev && \
    rm -rf /var/lib/apt/lists/*

# === РАБОЧАЯ ДИРЕКТОРИЯ ===
WORKDIR /app

# === КОПИРУЕМ И УСТАНОВЛИВАЕМ ПИП-ЗАВИСИМОСТИ ===
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --default-timeout=200 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt && \
    pip install --no-cache-dir "uvicorn[standard]" && \
    echo '✅ Зависимости установлены'

# === КОПИРУЕМ КОД ПРИЛОЖЕНИЯ ===
COPY main.py ./
COPY Wuglarst/ ./Wuglarst/
COPY data/ ./data/
COPY models/ ./models/  

# === ВАЛИДАЦИЯ (оставляем как есть) ===
RUN ls -la /app/models/ && \
    if [ ! -f /app/models/chat_model.pth ]; then \
        echo "❌ Ошибка: файл chat_model.pth отсутствует!"; \
        exit 1; \
    fi && \
    echo "✅ Модель найдена: /app/models/chat_model.pth"

# === ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0

# === ПЕРЕД ЗАПУСКОМ: проверяем, что main:app импортируется ===
RUN python -c "from main import app; print('✅ Приложение импортировано')" || (echo "❌ Ошибка импорта" && exit 1)

# === ОТКРЫВАЕМ ПОРТ ===
EXPOSE ${PORT}

# === HEALTHCHECK (с улучшенными настройками) ===
HEALTHCHECK --interval=15s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# === 🟢 КОМАНДА ЗАПУСКА ===
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]