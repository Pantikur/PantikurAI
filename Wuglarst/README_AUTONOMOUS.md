# 🚀 Wuglarst — Автономный Сервер для 13 ИИ-учёных

**Wuglarst Autonomous Server** — постоянный онлайн-сервер для наблюдения за работой 13 девочек (12 + Сидни) 24/7.

## 🎯 Возможности

- ✅ **Постоянная работа** — сервер работает даже когда вы выключили компьютер
- ✅ **Автозапуск** — запускается при старте Windows
- ✅ **Автосохранение** — состояние сохраняется каждые 5 минут
- ✅ **Автосброс** — перезапуск при падении
- ✅ **13 девочек** — поддержка Сидни (игровой движок)
- ✅ **WebSocket** — реального времени обновления
- ✅ **REST API** — полный интерфейс
- ✅ **Мониторинг** — проверка здоровья сервера
- ✅ **Визуальный интерфейс** — веб-панель управления

## 📁 Структура

```
Wuglarst/
├── server_autonomous.py    # Главный автономный сервер
├── daemon.py               # Демон для фоновой работы
├── server.py               # Старый сервер (сохранён)
├── naoto_integration.py    # Интеграция с Наото
├── start.bat               # Быстрый запуск
├── static/                 # Веб-интерфейс
│   └── index.html
├── data/                   # Автосохранение
│   └── system_state.json
└── logs/                   # Логи
    ├── wuglarst_daemon.log
    └── daemon.log
```

## 🚀 Быстрый Старт

### Вариант 1: Простой запуск (для тестирования)

```bash
cd Wuglarst
python server_autonomous.py
```

Сервер запустится на `http://localhost:8001`

### Вариант 2: Автономный режим (для постоянной работы)

```bash
cd Wuglarst
python daemon.py start
```

### Вариант 3: Установка как служба Windows

```bash
cd Wuglarst
python daemon.py install
```

## ⚙️ Настройка

### 1. Установка зависимостей

```bash
pip install fastapi uvicorn pydantic
```

### 2. Переменные окружения (опционально)

```bash
# Хост сервера
set WUGLARST_HOST=0.0.0.0

# Порт сервера
set WUGLARST_PORT=8001
```

### 3. Автозапуск при старте Windows

```bash
python daemon.py install
```

Создаёт файл автозапуска в:
```
C:\Users\YOUR_USER\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Wuglarst_start.bat
```

## 📡 API

### Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Веб-интерфейс |
| GET | `/api/status` | Полный статус системы |
| GET | `/health` | Проверка здоровья сервера |
| POST | `/api/scientist/{name}/update` | Обновить состояние |
| POST | `/api/scientist/{name}/event` | Добавить событие |
| POST | `/api/scientist/{name}/online` | Отметить онлайн |
| POST | `/api/scientist/{name}/offline` | Отметить оффлайн |
| POST | `/api/demo/populate` | Демо-данные |
| WS | `/ws` | WebSocket |

### Примеры

#### Обновить состояние Сидни

```python
import requests
from datetime import datetime

requests.post(
    "http://localhost:8001/api/scientist/Сидни/update",
    json={
        "name": "Сидни",
        "avatar": "🎮",
        "status": "working",
        "current_task": "Цикл 42 | Знаний: 3.2",
        "personality": {
            "перфекционизм": 75,
            "инновационность": 80
        },
        "last_activity": datetime.now().isoformat(),
        "x": 500,
        "y": 400,
        "autonomy_level": "L3",
        "engines_active": 8
    }
)
```

#### Получить статус

```python
import requests

response = requests.get("http://localhost:8001/api/status")
print(response.json())
```

#### Проверка здоровья

```python
import requests

response = requests.get("http://localhost:8001/health")
print(response.json())
# {"status": "healthy", "scientists": 13, "online": 8, ...}
```

## 🎮 Интеграция с Сидни

### Автоматическая

Сидни автоматически подключается к Wuglarst при запуске:

```python
from sidney import SidneyCore

sidney = SidneyCore()
sidney.initialize()  # Автоматически проверяет Wuglarst
sidney.start()
```

### Ручная

```python
from sidney.wuglarst_integration import WuglarstClient

client = WuglarstClient(host="localhost", port=8001)

# Обновить статус
client.update_status(
    status="working",
    current_task="Цикл 100 | Знаний: 4.1"
)

# Подключиться к девочкам
sisters = client.connect_to_sisters()
print(f"Онлайн: {len(sisters)} девочек")
```

## 🔧 Управление демоном

```bash
# Запуск
python daemon.py start

# Остановка
python daemon.py stop

# Перезапуск
python daemon.py restart

# Статус
python daemon.py status

# Установка автозапуска
python daemon.py install

# Удаление автозапуска
python daemon.py uninstall

# Установка как служба Windows
python daemon.py service
```

## 📊 Статусы девочек

| Статус | Описание | Цвет |
|--------|----------|------|
| `working` | Работает | 🟢 Зелёный |
| `thinking` | Думает | 🔵 Синий |
| `idle` | Ожидание | ⚪ Серый |
| `error` | Ошибка | 🔴 Красный |
| `offline` | Оффлайн | ⚫ Тёмный |

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────┐
│           Wuglarst Autonomous Server         │
│                                             │
│  ┌─────────────┐  ┌──────────────────────┐  │
│  │ FastAPI     │  │  WebSocket Server    │  │
│  │ REST API    │  │  Real-time Updates   │  │
│  └──────┬──────┘  └──────────┬───────────┘  │
│         │                    │              │
│  ┌──────▼────────────────────▼───────────┐  │
│  │         WuglarstSystem                │  │
│  │  - 13 Scientists                      │  │
│  │  - Events Log                         │  │
│  │  - Auto-save (5 min)                  │  │
│  └──────────────┬────────────────────────┘  │
│                 │                           │
│  ┌──────────────▼────────────────────────┐  │
│  │       Background Tasks                │  │
│  │  - Health Monitor                     │  │
│  │  - Auto-save Loop                     │  │
│  │  - Heartbeat Check                    │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         ▲                  ▲
         │                  │
    ┌────┴────┐      ┌─────┴─────┐
    │ Sidney  │      │  Other    │
    │  (13th) │      │  Scientists│
    └─────────┘      └───────────┘
```

## 🛡️ Надёжность

- **Автосохранение** каждые 5 минут
- **Автоматический перезапуск** при падении
- **Логирование** всех событий
- **Health Check** каждые 30 секунд
- **Heartbeat** для мониторинга активности

## 📝 Логи

Логи сохраняются в:
```
logs/
├── wuglarst_daemon.log   # Логи демона
├── daemon.log            # Логи процесса
└── wuglarst.log          # Логи сервера
```

## 🔒 Безопасность

- CORS настроен для локального доступа
- API не требует аутентификации (локальная сеть)
- Для внешнего доступа настройте reverse proxy (nginx)

## 📞 Решение проблем

### Сервер не запускается

```bash
# Проверьте порт
netstat -ano | findstr :8001

# Освободите порт
taskkill /F /PID <PID>
```

### Сидни не подключается

```bash
# Проверьте Wuglarst
curl http://localhost:8001/health

# Перезапустите
python daemon.py restart
```

### Данные не сохраняются

```bash
# Проверьте права на запись
dir data\wuglarst

# Создайте вручную
mkdir data\wuglarst
```

## 🎯 Следующие шаги

- [ ] Мобильное приложение для мониторинга
- [ ] Push-уведомления об ошибках
- [ ] Интеграция с Telegram ботом
- [ ] Статистика и аналитика
- [ ] Бэкап данных в облако
