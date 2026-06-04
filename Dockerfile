# === БАЗОВЫЙ ОБРАЗ ===
FROM python:3.11-slim

# === СИСТЕМНЫЕ ЗАВИСИМОСТИ ===
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
COPY main.py ./main.py
COPY Wuglarst/ ./Wuglarst/

# === КОПИРУЕМ ДАННЫЕ И МОДЕЛИ ===
COPY data/ ./data/
COPY models/ ./models/

# === ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# === ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА ИМПОРТА ===
RUN python -c "from main import app; print('✅ Приложение импортировано')" || (echo "❌ Ошибка импорта" && exit 1)

# === ОТКРЫВАЕМ ПОРТ ===
EXPOSE ${PORT}

# === HEALTHCHECK ===
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# === 🟢 КОМАНДА ЗАПУСКА ===
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]