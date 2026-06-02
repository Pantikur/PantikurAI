# === БАЗОВЫЙ ОБРАЗ ===
FROM python:3.11-slim

# === СИСТЕМНЫЕ ЗАВИСИМОСТИ ===
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        curl \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# === РАБОЧАЯ ДИРЕКТОРИЯ ===
WORKDIR /app

# === КОПИРУЕМ И УСТАНАВЛИВАЕМ ПИП-ЗАВИСИМОСТИ ===
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --default-timeout=200 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt && \
    pip install --no-cache-dir gunicorn uvicorn && \
    echo '✅ Зависимости установлены'

# === КОПИРУЕМ КОД ПРИЛОЖЕНИЯ ===
COPY . .

# === СОЗДАЁМ ДИРЕКТОРИИ ===
RUN mkdir -p models data logs

# === ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTORCH_ENABLE_MPS_FALLBACK=1

# === ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА ИМПОРТА ===
RUN python -c "from main import app; print('✅ Приложение импортировано')" || (echo "❌ Ошибка импорта" && exit 1)

# === ОТКРЫВАЕМ ПОРТ ===
EXPOSE ${PORT}

# === HEALTHCHECK — увеличенный таймаут ===
HEALTHCHECK --interval=30s --timeout=60s --start-period=180s --retries=5 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# === ENTRYPOINT: gunicorn + uvicorn worker — стабильный старт ===
ENTRYPOINT ["sh", "-c", "exec gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT} --timeout 300 --keep-alive 5 --access-logfile - --error-logfile -"]