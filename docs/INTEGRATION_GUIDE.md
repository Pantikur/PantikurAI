# 🌐 Интернет-доступ и автономное развитие

## ✅ Что реализовано

Обе системы — **Latislane** и **Celesta** — теперь имеют:

1. **Реальный доступ к интернету** через `WebResearcher`
2. **Автономное обучение** с периодическим запуском
3. **Саморазвитие** — анализ пробелов и улучшение знаний

---

## 📚 WebResearcher — Движок интернет-поиска

### Источники данных:

| Источник | API | Описание |
|----------|-----|----------|
| **Wikipedia** | REST API | Базовые знания на 200+ языках |
| **PubMed** | E-utilities NCBI | Медицинские исследования |
| **arXiv** | API | Научные预印本 (физика, биология, ИИ) |
| **Web scraping** | BeautifulSoup | Дополнительные источники |

### Как работает:

```
1. Получает тему для изучения
2. Параллельно ищет по 4 источникам
3. Извлекает факты из результатов
4. Сохраняет в кэш
5. Создаёт узлы знаний с уверенностью
```

### Пример результата:

```python
{
    "query": "human anatomy physiology",
    "sources": {
        "wikipedia": {"success": True, "content": "..."},
        "pubmed": {"success": True, "content": "..."},
        "arxiv": {"success": True, "content": "..."},
        "web": {"success": True, "content": "..."}
    },
    "facts": [
        {"text": "...", "source": "pubmed", "confidence": 0.7},
        {"text": "...", "source": "arxiv", "confidence": 0.7}
    ]
}
```

---

## 🤖 Автономное обучение

### Запуск:

```bash
# Latislane — автономное обучение каждые 15 минут
curl -X POST http://localhost:8000/latislane/autonomous \
  -H "Content-Type: application/json" \
  -d '{"interval_minutes": 15}'

# Celesta — автономное обучение каждые 15 минут
curl -X POST http://localhost:8000/celesta/autonomous \
  -H "Content-Type: application/json" \
  -d '{"interval_minutes": 15}'
```

### Что происходит:

1. Система определяет пробелы в знаниях
2. Запускает цикл обучения
3. Каждые N минут повторяет процесс
4. Сохраняет состояние в JSON

### Остановка:

Просто вызовите другой интервал или перезапустите сервер.

---

## 🔄 Саморазвитие

### Запуск:

```bash
# Latislane — саморазвитие
curl -X POST http://localhost:8000/latislane/self-improve

# Celesta — саморазвитие
curl -X POST http://localhost:8000/celesta/self-improve
```

### Что делает:

1. **Анализ пробелов** — находит темы с низким прогрессом
2. **Изучение новых тем** — запускает поиск по интернету
3. **Обновление низкой уверенности** — перепроверяет старые знания
4. **Верификация** — отмечает проверенные факты как `is_verified=True`

### Пример:

```
🔄 Запуск саморазвития...
📚 Изучение 5 новых тем...
🔄 Обновление 3 узлов с низкой уверенностью...
✅ Саморазвитие завершено
```

---

## 📊 Статус систем

### Latislane:

```python
{
    "overall_progress": 0.0375,  # 3.75%
    "total_topics": 40,
    "studied_topics": 1,
    "knowledge_nodes": 10,
    "web_researcher": True  # Интернет-поиск включён
}
```

### Celesta:

```python
{
    "overall_progress": 0.037,  # 3.7%
    "total_topics": 41,
    "studied_topics": 1,
    "knowledge_nodes": 10,
    "web_researcher": True  # Интернет-поиск включён
}
```

---

## ⚙️ Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `LATISLANE_REAL_WEB` | Включить реальный веб-поиск | `true` |
| `CELESTA_REAL_WEB` | Включить реальный веб-поиск | `true` |

### Переключение в демо-режим:

```bash
# Отключить интернет-поиск (использовать демо-данные)
export LATISLANE_REAL_WEB=false
export CELESTA_REAL_WEB=false
```

---

## 🚀 Полный цикл работы

```
1. Инициализация
   ↓
2. Определение пробелов в знаниях
   ↓
3. Запуск WebResearcher (4 источника)
   ↓
4. Извлечение фактов и создание узлов знаний
   ↓
5. Обновление прогресса
   ↓
6. Сохранение состояния в JSON
   ↓
7. Повтор через N минут (автономный режим)
```

---

## 📈 Примеры использования

### Проверка прогресса:

```bash
# Latislane
curl http://localhost:8000/latislane/status

# Celesta
curl http://localhost:8000/celesta/status
```

### Чат с системами:

```bash
# Latislane
curl -X POST http://localhost:8000/latislane/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "какой прогресс изучения анатомии?"}'

# Celesta
curl -X POST http://localhost:8000/celesta/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "какие последствия избыточного интима?"}'
```

### Статистика поиска:

```python
from web_researcher import WebResearcher

researcher = WebResearcher()
stats = researcher.get_stats()
# {
#     "total_searches": 150,
#     "successful": 142,
#     "failed": 8,
#     "success_rate": 0.947
# }
```

---

## 🔧 Технические детали

### Архитектура:

```
main.py (FastAPI)
├── latislane/
│   ├── latislane_core.py
│   └── internet_learning.py
│       └── WebResearcher (shared)
├── celesta/
│   ├── celesta_core.py
│   └── intimacy_learning.py
│       └── WebResearcher (shared)
└── web_researcher.py (общий модуль)
```

### Асинхронность:

- Все HTTP-запросы через `aiohttp`
- Параллельный поиск по 4 источникам
- Фоновые задачи через `asyncio.create_task()`

### Сохранение состояния:

- JSON файлы в `data/latislane/` и `data/celesta/`
- Автосохранение после каждого цикла
- Восстановление при перезапуске

---

## 🎯 Итог

Обе системы теперь:

✅ **Имеют доступ к интернету** — Wikipedia, PubMed, arXiv  
✅ **Автономно обучаются** — каждые N минут  
✅ **Саморазвиваются** — анализируют пробелы и улучшают знания  
✅ **Сохраняют состояние** — JSON файлы  
✅ **Работают в фоне** — через asyncio  

**Latislane** изучает тело, анатомию, бionic технологии  
**Celesta** изучает интимную жизнь, физиологию, последствия  

Обе системы растут и учатся каждый день! 🚀
