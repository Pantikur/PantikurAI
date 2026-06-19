# === БАЗОВЫЙ ОБРАЗ ===
FROM python:3.11-slim

# === СИСТЕМНЫЕ ЗАВИСИМОСТИ (включая curl и chrome) ===
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        curl \
        ca-certificates \
        libev-dev \
        libevent-dev \
        wget \
        gnupg \
        unzip \
        xvfb \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libc6 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libexpat1 \
        libfontconfig1 \
        libgbm1 \
        libgcc1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libstdc++6 \
        libx11-6 \
        libx11-xcb1 \
        libxcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxi6 \
        libxrandr2 \
        libxrender1 \
        libxss1 \
        libxtst6 \
        lsb-release \
        xdg-utils && \
    rm -rf /var/lib/apt/lists/*

# === ДОБАВЛЕНИЕ РЕПОЗИТОРИЯ CHROME И УСТАНОВКА (СОВРЕМЕННЫЙ МЕТОД) ===
RUN mkdir -p /etc/apt/keyrings && \
    wget -q -O- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# === РАБОЧАЯ ДИРЕКТОРИЯ ===
WORKDIR /app

# === КОПИРУЕМ И УСТАВЛИВАЕМ ПИП-ЗАВИСИМОСТИ ===
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
# Fallback для переменных (если .env не подхватился в Timeweb Cloud)
# GIGACHAT_TOKEN и RETRAIN_TOKEN должны быть заданы в настройках платформы

# === ПЕРЕД ЗАПУСКОМ: проверяем, что main:app импортируется ===
RUN python -c "from main import app; print('✅ Приложение импортировано')" || (echo "❌ Ошибка импорта" && exit 1)

# === ОТКРЫВАЕМ ПОРТ ===
EXPOSE ${PORT}

# === HEALTHCHECK (увеличен start-period для тяжёлой инициализации: модель + Chrome) ===
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# === 🟢 КОМАНДА ЗАПУСКА ===
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]