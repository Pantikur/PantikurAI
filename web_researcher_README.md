# 🌐 WebResearcher — Движок интернет-поиска

**WebResearcher** — общий исследователь интернета для Latislane и Celesta.

## 🔍 Источники данных

1. **Wikipedia API** — базовые знания на 200+ языках
2. **PubMed API** — медицинские исследования (NCBI)
3. **arXiv API** — научные预印本 по физике, биологии, ИИ
4. **Web scraping** — дополнительные источники через BeautifulSoup

## 🚀 Использование

```python
from web_researcher import WebResearcher

# Инициализация
researcher = WebResearcher()

# Поиск по теме
results = await researcher.search_all_sources("human anatomy")

# Полный цикл обучения
learning = await researcher.learn_from_search("skeletal system")

# Статистика
stats = researcher.get_stats()
```

## 📊 Результаты

```python
{
    "query": "human anatomy",
    "sources": {
        "wikipedia": {
            "content": "...",
            "snippets": [...],
            "success": True
        },
        "pubmed": {
            "content": "...",
            "article_ids": [...],
            "success": True
        },
        "arxiv": {
            "content": "...",
            "articles": [...],
            "success": True
        },
        "web": {
            "content": "...",
            "success": True
        }
    }
}
```

## 🌐 API Endpoints

### Latislane

```bash
# Автономное обучение
curl -X POST http://localhost:8000/latislane/autonomous \
  -H "Content-Type: application/json" \
  -d '{"interval_minutes": 10}'

# Саморазвитие
curl -X POST http://localhost:8000/latislane/self-improve
```

### Celesta

```bash
# Автономное обучение
curl -X POST http://localhost:8000/celesta/autonomous \
  -H "Content-Type: application/json" \
  -d '{"interval_minutes": 10}'

# Саморазвитие
curl -X POST http://localhost:8000/celesta/self-improve
```

## ⚙️ Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `LATISLANE_REAL_WEB` | Включить реальный веб-поиск | `true` |
| `CELESTA_REAL_WEB` | Включить реальный веб-поиск | `true` |

## 📈 Статистика

```python
{
    "total_searches": 150,
    "successful": 142,
    "failed": 8,
    "cache_size": 45,
    "success_rate": 0.947
}
```

## 🛠️ Зависимости

- `aiohttp` — асинхронный HTTP клиент
- `beautifulsoup4` — парсинг HTML
- `lxml` — XML парсер (для PubMed/arXiv)

## 📄 Лицензия

MIT License

---

**WebResearcher v0.1.0** — Исследуем интернет. Учимся каждый день. 🌐
