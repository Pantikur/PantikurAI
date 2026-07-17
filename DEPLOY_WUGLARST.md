# 🚀 Деплой Wuglarst на Timeweb

## 📋 Что настроено

✅ **Dockerfile.wuglarst** — образ для Wuglarst
✅ **docker-compose.yml** — два сервиса: chatbot (8000) + wuglarst (8001)
✅ **.env** — переменные WUGLARST_HOST и WUGLARST_PORT
✅ **.dockerignore** — исключение ненужных файлов

---

## 🎯 Доступ к серверу

После деплоя:

| Сервис | URL | Порт |
|--------|-----|------|
| **Chatbot API** | `https://wuglarst.ru` | 8000 |
| **Wuglarst** | `https://wuglarst.ru:8001` | 8001 |

Или по IP:
- `http://85.239.63.58:8001` — Wuglarst

---

## 📦 Команды деплоя

### 1. Проверка локально

```bash
# Сборка образов
docker-compose build

# Запуск
docker-compose up -d

# Проверка
docker-compose ps
curl http://localhost:8001/health
```

### 2. Деплой на Timeweb

```bash
# Пуш в git (уже сделано)
git push

# Timeweb автоматически перезапустит деплой
# Или перезапустите вручную в панели
```

### 3. Логи

```bash
# Все логи
docker-compose logs -f

# Только Wuglarst
docker-compose logs -f wuglarst

# Только Chatbot
docker-compose logs -f chatbot-api
```

### 4. Перезапуск

```bash
# Перезапуск Wuglarst
docker-compose restart wuglarst

# Перезапуск всего
docker-compose restart
```

---

## 🔧 Структура сервисов

```
docker-compose.yml:
├── chatbot-api (порт 8000)
│   ├── Dockerfile
│   ├── main.py
│   └── Все модели и данные
│
└── wuglarst (порт 8001) ⭐ НОВЫЙ
    ├── Dockerfile.wuglarst
    ├── server_autonomous.py
    ├── daemon.py
    └── data/wuglarst/ (автосохранение)
```

---

## 📊 Мониторинг

### Health Check

```bash
# Wuglarst
curl http://localhost:8001/health

# Chatbot
curl http://localhost:8000/health
```

### Статус

```bash
# Все сервисы
docker-compose ps

# Детали
docker inspect pantikur-wuglarst
```

---

## 🎮 API Wuglarst

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Веб-интерфейс |
| GET | `/api/status` | Статус системы |
| GET | `/health` | Проверка здоровья |
| POST | `/api/demo/populate` | Демо-данные |
| WS | `/ws` | WebSocket |

---

## 🔄 CI/CD

Timeweb автоматически:
1. Собирает образ при пуше в git
2. Запускает контейнеры
3. Проверяет healthcheck
4. Перезапускает при ошибках

---

## 🛡️ Безопасность

- Порты 3389, 587, 2525, 465, 25, 53413, 389 — закрыты (TIMWEB)
- Порт 8001 — открыт для Wuglarst
- CORS настроен на `*` (для локальной разработки)

---

## 💡 Советы

### Если Wuglarst не запускается

```bash
# Проверьте логи
docker-compose logs wuglarst

# Пересоберите
docker-compose build wuglarst
docker-compose up -d wuglarst
```

### Если порт 8001 недоступен

```bash
# Проверьте что порт открыт
docker port pantikur-wuglarst

# Проверьте firewall
curl http://85.239.63.58:8001/health
```

### Масштабирование

Если нужно больше ресурсов:

```yaml
# docker-compose.yml
wuglarst:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
```

---

## 📞 Поддержка

- Timeweb Cloud: https://timeweb.cloud/docs
- Логи: `docker-compose logs wuglarst`
- Статус: `http://85.239.63.58:8001/health`
