# syntax=docker/dockerfile:1.4
# === БАЗОВЫЙ ОБРАЗ ===
FROM python:3.11-slim

# === СИСТЕМНЫЕ ЗАВИСИМОСТИ ===
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg \
        wget \
        fonts-liberation \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libexpat1 \
        libfontconfig1 \
        libgbm1 \
        libglib2.0-0 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
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
        xdg-utils && \
    # === УСТАНОВКА GOOGLE CHROME (современный метод GPG) ===
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# === CHROMEDRIVER (без Chrome — используем undetected-chromedriver) ===
# Chrome не нужен для undetected-chromedriver
# selenium-manager сам скачает нужную версию

# === РАБОЧАЯ ДИРЕКТОРИЯ ===
WORKDIR /app

# === УСТАНОВКА Python ЗАВИСИМОСТЕЙ ===
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
        --default-timeout=300 \
        --retries=10 \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        -r requirements.txt && \
    pip install --no-cache-dir "uvicorn[standard]" && \
    echo '✅ Зависимости установлены'

# === КОПИРУЕМ КОД ПРИЛОЖЕНИЯ ===
COPY main.py ./
COPY Wuglarst/ ./Wuglarst/
COPY utils/ ./utils/
COPY data/ ./data/
COPY models/ ./models/
COPY web_researcher.py ./
COPY web_researcher_demo.py ./
COPY web_researcher_README.md ./

# === КОПИРУЕМ ВСЕ МОДУЛИ УЧЁНЫХ (12 девочек) ===
COPY hanako/ ./hanako/
COPY fuyuki/ ./fuyuki/
COPY lucy/ ./lucy/
COPY futaba/ ./futaba/
COPY shiori/ ./shiori/
COPY nobuka/ ./nobuka/
COPY akva/ ./akva/
COPY latislane/ ./latislane/
COPY celesta/ ./celesta/
COPY naoto/ ./naoto/
COPY yu/ ./yu/
COPY ayiko/ ./ayiko/
COPY scientists_network/ ./scientists_network/
COPY autonomous_girls_v2.py ./

# === ЗАГРУЗКА МОДЕЛИ ИЗ HUGGINGFACE ===
RUN pip install --no-cache-dir huggingface_hub && \
    python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Pantikur/Wuglarst', local_dir='models/rugpt3')" 2>/dev/null || echo "⚠️ Модель не загружена (нет сети)"

# === ВАЛИДАЦИЯ ===
RUN if [ -d /app/models/rugpt3 ] && [ "$(ls -A /app/models/rugpt3)" ]; then \
        echo "✅ RUGPT3 найдена в /app/models/rugpt3"; \
    else \
        echo "⚠️ RUGPT3 не найдена — будет загружена при запуске из HuggingFace"; \
    fi

# === ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV SELENIUM_REMOTE_URL=""
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PYTHONPATH="/app:${PYTHONPATH}"

# === ПРОВЕРКА ИМПОРТА ===
RUN python -c "from main import app; print('✅ Приложение импортировано')" || (echo "❌ Ошибка импорта" && exit 1)

# === ОТКРЫВАЕМ ПОРТ ===
EXPOSE ${PORT}

# === HEALTHCHECK ===
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# === КОМАНДА ЗАПУСКА ===
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]