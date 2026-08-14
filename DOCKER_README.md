# 🐳 Docker — Развёртывание Pantikur ChatBot

## 📋 Быстрый старт

### 1. Локальный запуск (без Docker)

```bash
python run_local.py
```

Или с кастомным портом:

```bash
python run_local.py --port 9000
```

### 2. Docker Compose (локально)

```bash
docker-compose -f docker-compose.local.yml up --build
```

### 3. Docker Compose (TimeWeb)

```bash
docker-compose -f docker-compose.timeweb.yml up -d --build
```

---

## 🔧 Настройка Docker

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `HOST` | Хост для прослушивания | `0.0.0.0` |
| `PORT` | Порт | `8000` |
| `PYTHONUNBUFFERED` | Отключить буферизацию логов | `1` |
| `AUTO_GIRLS_ENABLED` | Включить автономных девочек | `true` |
| `AUTO_BOOK_LEARNING` | Автообучение из книг | `true` |
| `AUTO_RETRAIN` | Авто-ретрейн модели | `true` |

### Тома (Volumes)

| Путь контейнера | Путь хоста | Назначение |
|-----------------|------------|------------|
| `/app/data` | `./data` | Данные чата, токенизатор |
| `/app/logs` | `./logs` | Логи приложения |
| `/app/models/qwen2.5-3b` | `./models/qwen2.5-3b` | Модель Qwen2.5-3B |
| `/app/shiori/polygon` | `./shiori/polygon` | Данные полигона Шиори |

---

## 🏥 Health Check

### Endpoint

```
GET http://localhost:8000/health
```

### Пример ответа

```json
{
  "status": "ok",
  "bot_ready": true,
  "girls_enabled": true,
  "girls_count": 12,
  "timestamp": "2026-08-15T00:00:00",
  "blocked_ips": 5,
  "rate_limit_active": true
}
```

### Настройка в Dockerfile

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

**Важно:** `--start-period=120s` — время на загрузку модели (5-15 минут).

---

## 🐛 Решение проблем

### Проблема: Контейнер не проходит healthcheck

**Причины:**
1. Модель загружается 5-15 минут, а healthcheck ждёт только 60 секунд
2. Uvicorn не запускается из-за ошибки импорта
3. Порт 8000 уже занят

**Решения:**

1. **Увеличить start-period:**
   ```dockerfile
   HEALTHCHECK --start-period=300s
   ```

2. **Проверить логи:**
   ```bash
   docker logs pantikur-chatbot
   ```

3. **Проверить доступность:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Пересобрать образ:**
   ```bash
   docker-compose -f docker-compose.local.yml build --no-cache
   ```

### Проблема: Модель не загружается

**Решение:** Загрузить модель вручную:

```bash
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='Qwen/Qwen2.5-3B-Instruct',
    local_dir='models/qwen2.5-3b',
    local_dir_use_symlinks=False,
)
"
```

### Проблема: Ошибка импорта main.py

**Причины:**
- Отсутствуют зависимости
- Ошибка в коде main.py
- Неправильный PYTHONPATH

**Решение:**
```bash
# Проверить зависимости
docker exec -it pantikur-chatbot python -c "import fastapi; import uvicorn; print('OK')"

# Проверить импорт
docker exec -it pantikur-chatbot python -c "import main; print('OK')"
```

---

## 📊 Мониторинг

### Логи в реальном времени

```bash
docker logs -f pantikur-chatbot
```

### Статус контейнера

```bash
docker ps
docker inspect pantikur-chatbot
```

### Статус здоровья

```bash
docker inspect --format='{{.State.Health.Status}}' pantikur-chatbot
```

### Перезапуск

```bash
docker-compose -f docker-compose.local.yml restart
```

---

## 🚀 Production

### TimeWeb

1. Загрузить код на сервер
2. Создать `docker-compose.timeweb.yml`
3. Запустить:
   ```bash
   docker-compose -f docker-compose.timeweb.yml up -d --build
   ```

### Nginx (反向代理)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```
