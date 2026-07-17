# 🌟 Wuglarst — Визуальное пространство ИИ-ученых

**Wuglarst** — это веб-интерфейс для наблюдения за работой 12 ИИ-девушек в реальном времени.

## 🎯 Возможности

- **Живая карта проекта** с аватарами ученых
- **Статус в реальном времени** (работает, думает, ожидает, ошибка)
- **Информация о личности** каждого ученого
- **Журнал событий** с историей действий
- **WebSocket** для мгновенных обновлений

## 🚀 Запуск

### 1. Установка зависимостей

```bash
pip install fastapi uvicorn httpx websockets
```

### 2. Запуск сервера

```bash
python -m wuglarst.server
```

Сервер запустится на `http://localhost:8001`

### 3. Открытие интерфейса

Открой браузер и перейди на:
```
http://localhost:8001
```

### 4. Загрузка демо-данных

Нажми кнопку **"🎮 Демо-данные"** в правом верхнем углу.

## 📡 API

### Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Главная страница |
| GET | `/api/status` | Полный статус системы |
| POST | `/api/scientist/{name}/update` | Обновить состояние ученого |
| POST | `/api/scientist/{name}/event` | Добавить событие |
| POST | `/api/demo/populate` | Загрузить демо-данные |
| WS | `/ws` | WebSocket для реального времени |

### Примеры использования

#### Обновление состояния ученого

```python
import httpx

httpx.post(
    "http://localhost:8001/api/scientist/Наото/update",
    json={
        "name": "Наото",
        "avatar": "📚",
        "status": "working",
        "current_task": "Анализ книги '1984'",
        "personality": {
            "empathy": 0.53,
            "cynicism": 0.50,
            "logic": 0.52,
        },
        "position": {"x": 200, "y": 300},
    }
)
```

#### Добавление события

```python
import httpx

httpx.post(
    "http://localhost:8001/api/scientist/Наото/event",
    json={
        "type": "task_update",
        "message": "📚 Наото: Нашла новую книгу для анализа"
    }
)
```

## 🎨 Визуализация

### Цвета статусов

- 🟢 **Зеленый** — Работает (working)
- 🔵 **Синий** — Думает (thinking)
- ⚪ **Серый** — Ожидание (idle)
- 🔴 **Красный** — Ошибка (error)

### Позиции на карте

Каждый ученый имеет координаты `(x, y)` на карте проекта.
По умолчанию используется сетка 4x3.

## 🔌 Интеграция с Наото

Наото может отправлять данные в Вугларст через `WuglarstClient`:

```python
from wuglarst.naoto_integration import get_wuglarst_client

client = get_wuglarst_client()
await client.update_status(
    name="Наото",
    status="working",
    current_task="Анализ лора книги",
    personality={"empathy": 0.53, "logic": 0.52}
)
```

## 📁 Структура проекта

```
wuglarst/
├── server.py              # FastAPI сервер
├── naoto_integration.py   # Интеграция с Наото
└── static/
    ├── index.html         # Главная страница
    ├── css/
    │   └── style.css      # Стили
    └── js/
        └── app.js         # Логика интерфейса
```

## 🛠️ Технологии

- **Backend**: FastAPI + Python 3.11
- **Frontend**: Чистый HTML/CSS/JavaScript
- **WebSocket**: Real-time обновления
- **HTTP**: REST API

## 🎯 Следующие шаги

- [ ] Интеграция со всеми 12 девочками
- [ ] Анимированные потоки данных между учеными
- [ ] Интерактивные элементы (клик по ученому → чат)
- [ ] Сохранение истории в базу данных
- [ ] Мобильная адаптация

## 📝 Лицензия

Проект является частью системы PantikurAI.
