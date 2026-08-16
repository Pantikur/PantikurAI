# syntax=docker/dockerfile:1.4
# ============================================================
# Оптимизированный Dockerfile для Pantikur ChatBot
# ============================================================
# Изменения:
# 1. Мультистадийная сборка (builder + production)
# 2. Загрузка модели перенесена в run-time (entrypoint.sh)
# 3. Убран Google Chrome (не нужен для undetected-chromedriver)
# 4. Убрана жёсткая проверка импорта при сборке
# 5. Оптимизирован размер образа

# === ЭТАП 1: СБОРКА ЗАВИСИМОСТЕЙ (кэширование pip) ===
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
        --default-timeout=300 \
        --retries=10 \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        -r requirements.txt && \
    pip install --no-cache-dir "uvicorn[standard]"

# === ЭТАП 2: ПРОДУКЦИОННЫЙ ОБРАЗ ===
FROM python:3.11-slim AS production

# === СИСТЕМНЫЕ ЗАВИСИМОСТИ (минимальный набор для Selenium/Web) ===
# === Google Chrome устанавливается здесь (build-time), а не в entrypoint ===
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
    wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y --no-install-recommends /tmp/chrome.deb && \
    rm -f /tmp/chrome.deb && \
    rm -rf /var/lib/apt/lists/*

# === КОПИРУЕМ ЗАВИСИМОСТИ ИЗ BUILDER ===
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# === РАБОЧАЯ ДИРЕКТОРИЯ ===
WORKDIR /app

# === СОЗДАЁМ ДИРЕКТОРИЮ ДЛЯ ЛОГОВ ===
RUN mkdir -p /app/logs

# === КОПИРУЕМ КОД ПРИЛОЖЕНИЯ ===
COPY main.py ./
COPY barston_lore_loader.py ./
COPY train.py ./
COPY retrain.py ./
COPY auto_retrain.py ./
COPY generate_training_data.py ./
COPY bot_learns_from_gigachat.py ./
COPY Wuglarst/ ./Wuglarst/
COPY utils/ ./utils/
COPY data/ ./data/
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
COPY auto_learn_cycle.py ./
COPY autonomous_girls_v2.py ./
COPY orchestrator_v3.py ./
COPY orchestrator.py ./
COPY humanity_core.py ./

# === КОПИРУЕМ ENTRYPOINT ===
COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# === ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ ===
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV SELENIUM_REMOTE_URL=""
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

# === ОТКРЫВАЕМ ПОРТ ===
EXPOSE ${PORT}

# === HEALTHCHECK ===
# /ping — мгновенный ответ 200, проверяет что uvicorn слушает порт 8000
# start-period=120s — даём время entrypoint.sh на установку Chrome и запуск uvicorn
# timeout=10s — увеличен для надёжности, interval=15s — чаще проверяем
HEALTHCHECK --interval=15s --timeout=10s --retries=10 --start-period=120s \
    CMD curl -f http://localhost:${PORT}/ping || exit 1

# === КОМАНДА ЗАПУСКА (через entrypoint с загрузкой модели) ===
CMD ["./entrypoint.sh"]