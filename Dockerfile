# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc curl && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt && \
    echo '✅ Все зависимости установлены'

# Копируем код приложения
COPY . .

# Создаём необходимые директории
RUN mkdir -p models data

# Экспортируем переменные окружения
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Проверяем Uvicorn
RUN python -c "import uvicorn" && \
    echo '✅ Uvicorn импортирован успешно'

# === Скачивание модели при сборке (рекомендуется для продакшена) ===
# Чтобы не ждать при первом запуске
RUN echo '📥 Скачиваю модель при сборке...' && \
    curl -# -L 'https://drive.google.com/uc?export=download&id=1POLpxWHyN4_dYb3Sl1IUZuK01kbp3-1i' -o models/chat_model.pth || \
    (echo '❌ Не удалось скачать модель!' && exit 1)

# === Если есть данные — конвертируем ===
# COPY data/training_pairs.jsonl data/  # раскомментируй, если кладёшь в репозиторий
# RUN if [ -f 'data/training_pairs.jsonl' ] && [ ! -f 'data/chat_data.pkl' ]; then \
#     python convert_data.py; \
# fi

# Прямо указываем команду (лучше для хостингов)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]