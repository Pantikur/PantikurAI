# Research Monitor API — Мониторинг исследований учёных

## Обзор

Research Monitor позволяет запускать, останавливать и наблюдать за процессом исследований **четырнадцать** учёных:

- **Ханако** — исследование гравитации
- **Фуюки** — исследование атмосферного электричества
- **Люси** — проектирование двигателей
- **Футаба** — автономное саморазвитие и правовые исследования
- **Шиори** — иммунная система и безопасность
- **Нобука** — анализ и улучшения проекта
- **Латислейн** — изучение тела и анатомия
- **Селеста** — изучение интимной жизни и физиологии
- **Аква** — математика, физика, аэродинамика, сопротивление материалов
- **Юи** — сознание, перенос разума, оцифровка души
- **Наото** — чтение книг, изучение мысли автора в тексте, изучение лора книги, изучение повидения всех героев в книге, изучение построения сюжета книги, изучение скрытого (фантомного, мысленного) повествования и мысли книги
- **Айка** — изучать основы рисунка, осваивать техническую графику, развивать навыки 3D-моделирования
- **Сидни** — игровой движок
- **Кристи** — видеоредактор и создание видио

## Scientists Network — Коммуникация между учёными

Все учёные подключены к **Scientists Network** и могут:

- ✅ Отправлять прямые сообщения (peer-to-peer)
- ✅ Отправлять групповые сообщения (broadcast)
- ✅ Передавать данные (теории, вычисления, проекты)
- ✅ Координировать совместную работу
- ✅ Автоматически болтать когда "скучно" (10% шанс каждый цикл)
- ✅ Использовать интернет для исследований (Аква, Юи)

### Типы сообщений

| Тип | Описание | Пример |
|-----|----------|--------|
| `message` | Обычное сообщение | "Привет всем! Как дела?" |
| `question` | Вопрос | "Кто работал с гравитацией?" |
| `answer` | Ответ | "Да, я изучала это!" |
| `greeting` | Приветствие | "Всем привет!" |
| `theory` | Теория | "Построена новая теория" |
| `calculation` | Вычисление | "Результат: 42.5" |
| `improvement` | Улучшение | "Применено улучшение" |
| `boredom` | Скучно | "Мне немного скучно..." |
| `coordination` | Координация | "Предлагаю collaboration!" |
| `security_alert` | Опасность | "Обнаружена угроза!" |

## Новые учёные

### Юи — Перенос сознания и души

Юи изучает:
- Подключение человека к компьютеру (BCI)
- Перенос разума в цифровой мир (mind uploading)
- Оцифровку души (soul digitization)
- Цифровое перерождение (digital reincarnation)
- Мост между физическим и цифровым мирами

**API:**
```bash
# Данные Юи
curl http://localhost:8000/research/yu/data
```

**Ответ:**
```json
{
  "status": "ok",
  "scientist": "yu",
  "consciousness_models": [
    {
      "name": "Квантовая модель сознания",
      "type": "hybrid",
      "complexity": 0.95,
      "description": "Модель сознания для consciousness_transfer"
    }
  ],
  "embodiments": [
    {
      "name": "Цифровой аватар сознания",
      "embodiment_type": "avatar",
      "capabilities": ["самоосознание", "память", "эмоции"]
    }
  ],
  "transfer_records": [
    {
      "transfer_type": "full_mind_upload",
      "source": "человек_А",
      "target": "server_01",
      "success": true,
      "timestamp": "2026-07-11T23:00:00"
    }
  ]
}
```

### Аква — Физика + Интернет

Аква имеет доступ к интернету для поиска научных данных:
- Каждые 3 цикла — веб-поиск по научным базам
- Поиск: Riemann hypothesis, quantum gravity, aerodynamics
- Интеграция найденных данных в исследования

**Пример:**
```
📚 Найдена статья: 'Riemann hypothesis proof 2026' - 15 результатов
🔬 Исследование: 'quantum gravity latest developments' - 8 новых papers
🌐 Обзор: 'supersonic aerodynamics breakthrough' - 23 источника
```

## Примеры коммуникации

**Обмен теориями:**
```
Ханако → ВСЕ: 🔬 Новая теория: Петлевая квантовая гравитация
Аква → Ханако: 📋 Запрос данных: theories
Ханако → Аква: ✅ Отправила 15 теорий
```

**Юи и наука:**
```
Юи → ВСЕ: 🧠 Новая модель сознания: Квантовое сознание
Юи → Аква: 📋 Запрос данных: physics_data
Аква → Юи: 🧮 Вычисление: E=mc^2 = 9×10^16 J
Юи → Аква: 🤝 Предлагаю collaboration!
```

**Координация:**
```
Люси → Аква: ❓ Кто работал с аэродинамикой?
Аква → ВСЕ: 💡 Я изучала уравнения Навье-Стокса!
Люси → Аква: 🤝 Предлагаю collaboration!
```

**Болтовня (автоматическая):**
```
😴 futaba: Мне немного скучно... Кто-нибудь хочет поболтать?
🎉 shiori: Не скучай! Давай обсудим мои последние результаты!
💬 nobuka: Я тут подумала о новых исследованиях...
```
GET /research/status
```

Возвращает статус всех ядер учёных.

**Пример ответа:**
```json
{
  "status": "ok",
  "research": {
    "total_cores": 3,
    "running_count": 2,
    "cores": {
      "hanako": {
        "name": "Hanako",
        "is_running": true,
        "metrics": {
          "theories_built": 5,
          "calculations_run": 5,
          "papers_studied": 25
        }
      },
      "fuyuki": {
        "name": "Fuyuki",
        "is_running": true,
        "metrics": {
          "theories_built": 3,
          "calculations_run": 3,
          "papers_studied": 15
        }
      },
      "lucy": {
        "name": "Lucy",
        "is_running": false,
        "metrics": {
          "designs_created": 0,
          "calculations_run": 0,
          "papers_studied": 0
        }
      }
    }
  }
}
```

### Запуск исследований
```
POST /research/start/{scientist}
```

Параметры:
- `scientist` — имя учёного: `hanako`, `fuyuki`, `lucy`, `futaba`, `shiori`, `nobuka`, `latislane`, `celest`, `akva`

### Остановка исследований
```
POST /research/stop/{scientist}
```

## Детальный мониторинг

### Полная сводка по ядру
```
GET /research/{scientist}/summary
```

Возвращает:
- Статус ядра
- События
- Логи
- Теории
- Вычисления
- Статьи
- История исследований

### Детальный статус
```
GET /research/{scientist}/status
```

### События
```
GET /research/{scientist}/events?limit=50&event_type=THEORY
```

Параметры:
- `limit` — максимальное количество событий (по умолчанию 50)
- `event_type` — фильтр по типу: `STARTED`, `STOPPED`, `CYCLE`, `THEORY`, `CALCULATION`, `PAPERS`, `DISCOVERY`, `ERROR`

### Логи
```
GET /research/{scientist}/logs?limit=100
```

### Теории
```
GET /research/{scientist}/theories?limit=20
```

### Вычисления
```
GET /research/{scientist}/calculations?limit=20
```

### Статьи
```
GET /research/{scientist}/papers?limit=20
```

### История исследований
```
GET /research/{scientist}/history?limit=50
```

## Поток событий в реальном времени (SSE)

### События одного ядра
```
GET /research/live/{scientist}
```

Возвращает Server-Sent Events с событиями в реальном времени.

**Поддерживаемые типы событий:**
- `STARTED` / `STOPPED` — запуск/остановка
- `CYCLE` — начало цикла исследований
- `THEORY` — построение новой теории (Ханако, Фуюки)
- `CALCULATION` — выполнение вычисления (Ханако, Фуюки, Люси)
- `DESIGN` — проектирование двигателя (Люси)
- `PAPERS` — обнаружение новых статей
- `DISCOVERY` — находка (секреты гравитации/молний)
- `CHANGE` — применение изменения (Футаба, Нобука)
- `THREAT` — обнаружение угрозы (Шиори)
- `PATCH` — применение патча (Шиори)
- `IMPROVEMENT` — улучшение проекта (Нобука)
- `ANATOMY` — исследование анатомии (Латислейн)
- `INTIMACY` — изучение интимной жизни (Селеста)
- `THEORY` — построение теории (Аква)
- `CALCULATION` — выполнение вычисления (Аква)
- `ERROR` — ошибка
- `status` — статус ядра

### События всех ядер
```
GET /research/live/all
```

## Примеры использования

### Запуск Ханако и мониторинг
```bash
# Запуск
curl -X POST http://localhost:8000/research/start/hanako

# Проверка статуса
curl http://localhost:8000/research/status

# Просмотр событий
curl http://localhost:8000/research/hanako/events

# Просмотр теорий
curl http://localhost:8000/research/hanako/theories

# SSE поток (в реальном времени)
curl http://localhost:8000/research/live/hanako
```

### Запуск Футабы и мониторинг
```bash
# Запуск
curl -X POST http://localhost:8000/research/start/futaba

# Просмотр изменений
curl http://localhost:8000/research/futaba/history

# SSE поток
curl http://localhost:8000/research/live/futaba
```

### Запуск Шиори и мониторинг
```bash
# Запуск
curl -X POST http://localhost:8000/research/start/shiori

# Просмотр угроз
curl http://localhost:8000/research/shiori/history

# SSE поток
curl http://localhost:8000/research/live/shiori
```

### Запуск Нобука и мониторинг
```bash
# Запуск
curl -X POST http://localhost:8000/research/start/nobuka

# Просмотр улучшений
curl http://localhost:8000/research/nobuka/history

# SSE поток
curl http://localhost:8000/research/live/nobuka
```

### Запуск Селесты и мониторинг
```bash
# Запуск
curl -X POST http://localhost:8000/research/start/celest

# Просмотр отчёта
curl http://localhost:8000/research/celest/summary

# SSE поток
curl http://localhost:8000/research/live/celest
```

### Запуск Аква и мониторинг
```bash
# Запуск
curl -X POST http://localhost:8000/research/start/akva

# Просмотр теорий
curl http://localhost:8000/research/akva/theories

# Просмотр вычислений
curl http://localhost:8000/research/akva/calculations

# SSE поток
curl http://localhost:8000/research/live/akva
```

## Scientists Network API

### Статус сети
```bash
# Получить статусScientists Network
curl http://localhost:8000/network/status
```

**Ответ:**
```json
{
  "status": "ok",
  "network": {
    "total_scientists": 9,
    "scientists": ["hanako", "fuyuki", "lucy", "futaba", "shiori", "nobuka", "latislane", "celest", "akva"],
    "total_messages": 142,
    "messages_by_type": {
      "message": 45,
      "theory": 30,
      "greeting": 20,
      "boredom": 15,
      "coordination": 10,
      "question": 12,
      "answer": 10
    },
    "messages_by_scientist": {
      "hanako": 35,
      "fuyuki": 28,
      "lucy": 22,
      "akva": 18
    }
  }
}
```

### История сообщений
```bash
# Получить последние 50 сообщений
curl http://localhost:8000/network/history?limit=50

# Фильтр по отправителю
curl http://localhost:8000/network/history?sender=hanako&limit=20
```

**Ответ:**
```json
{
  "status": "ok",
  "messages": [
    {
      "message_type": "greeting",
      "sender": "hanako",
      "recipient": "all",
      "content": "👋 hanako: Всем привет! Как дела?",
      "priority": "low",
      "timestamp": "2026-07-11T22:30:00",
      "message_id": "hanako_1234567890"
    }
  ],
  "count": 50
}
```

### Отправка сообщения
```bash
# Отправить сообщение всем
curl -X POST http://localhost:8000/network/send \
  -d "sender=hanako&recipient=all&content=Привет всем!&message_type=greeting"

# Отправить вопрос
curl -X POST http://localhost:8000/network/send \
  -d "sender=lucy&recipient=akva&content=Какие у тебя данные по аэродинамике?&message_type=question&priority=high"

# Отправить теорию
curl -X POST http://localhost:8000/network/send \
  -d "sender=akva&recipient=all&content=Новая теория квантовой гравитации&message_type=theory&priority=high"
```

### Примеры коммуникации

**Обмен теориями:**
```
Ханако → ВСЕ: 🔬 Новая теория: Петлевая квантовая гравитация
Аква → Ханако: 📋 Запрос данных: theories
Ханако → Аква: ✅ Отправила 15 теорий
```

**Координация:**
```
Люси → Аква: ❓ Кто работал с аэродинамикой?
Аква → ВСЕ: 💡 Я изучала уравнения Навье-Стокса!
Люси → Аква: 🤝 Предлагаю collaboration!
```

**Болтовня (автоматическая):**
```
😴 futaba: Мне немного скучно... Кто-нибудь хочет поболтать?
🎉 shiori: Не скучай! Давай обсудим мои последние результаты!
💬 nobuka: Я тут подумала о новых исследованиях...
```

### Просмотр результатов
```bash
# Полная сводка
curl http://localhost:8000/research/hanako/summary

# Логи
curl http://localhost:8000/research/hanako/logs

# История
curl http://localhost:8000/research/hanako/history
```

### Остановка
```bash
curl -X POST http://localhost:8000/research/stop/hanako
```

## Структура события

```json
{
  "event_type": "THEORY",
  "scientist": "hanako",
  "message": "Построена новая теория",
  "data": {
    "theory_name": "Петлевая квантовая гравитация",
    "category": "quantum",
    "scientific_value": 0.84
  },
  "timestamp": "2026-07-11T22:04:37.404000"
}
```

## Метрики

### Ханако (гравитация)
- `theories_built` — количество построенных теорий
- `calculations_run` — количество вычислений
- `papers_studied` — количество изученных статей
- `web_searches` — количество веб-поисков
- `gravity_secrets_found` — количество найденных секретов гравитации

### Фуюки (электричество)
- `theories_built` — количество построенных теорий
- `calculations_run` — количество вычислений
- `papers_studied` — количество изученных статей
- `web_searches` — количество веб-поисков
- `lightning_secrets_found` — количество найденных секретов молний

### Люси (двигатели)
- `designs_created` — количество спроектированных двигателей
- `calculations_run` — количество вычислений
- `papers_studied` — количество изученных статей
- `web_searches` — количество веб-поисков
- `hybrid_engines_designed` — количество спроектированных гибридных двигателей

### Футаба (саморазвитие)
- `changes_applied` — количество применённых изменений
- `cycles_completed` — количество завершённых циклов
- `improvements_applied` — количество улучшений
- `world_models_created` — количество созданных моделей мира
- `trial_grounds_score` — лучший результат на полигоне испытаний

### Шиори (безопасность)
- `threats_detected` — количество обнаруженных угроз
- `patches_applied` — количество применённых патчей
- `incidents_handled` — количество обработанных инцидентов
- `quarantined_files` — количество изолированных файлов
- `cycles_completed` — количество завершённых циклов защиты

### Нобука (улучшения)
- `improvements_applied` — количество применённых улучшений
- `files_analyzed` — количество проанализированных файлов
- `issues_found` — количество обнаруженных проблем
- `issues_fixed` — количество исправленных проблем
- `tests_generated` — количество сгенерированных тестов
- `refactors_done` — количество выполненных рефакторингов

### Латислейн (тело)
- `anatomy_studies` — количество проведённых исследований анатомии
- `body_designs_created` — количество созданных дизайнов тела
- `cycles_completed` — количество завершённых циклов
- `improvements_applied` — количество применённых улучшений

### Селеста (интимная жизнь)
- `research_cycles` — количество циклов исследований
- `knowledge_points` — количество изученных точек знаний
- `modules_studied` — количество изучённых модулей
- `overall_progress` — общий прогресс изучения (%)
- `event_log_count` — количество записанных событий

### Аква (математика, физика)
- `theories_built` — количество построенных теорий
- `calculations_run` — количество выполненных вычислений
- `improvements_applied` — количество применённых улучшений
- `cycles_completed` — количество завершённых циклов
- `math_topics_explored` — изучено тем по математике
- `physics_topics_explored` — изучено тем по физике
- `aerodynamics_topics_explored` — изучено тем по аэродинамике
- `mechanics_topics_explored` — изучено тем по сопротивлению материалов

## Параметры scientist

Допустимые значения параметра `{scientist}`:
- `hanako` — Ханако (гравитация)
- `fuyuki` — Фуюки (электричество)
- `lucy` — Люси (двигатели)
- `futaba` — Футаба (саморазвитие)
- `shiori` — Шиори (безопасность)
- `nobuka` — Нобука (улучшения)
- `latislane` — Латислейн (тело)
- `celest` — Селеста (интимная жизнь)
