# 🧬 Latislane — Система изучения тела и проектирования

**Latislane** — автономная система, изучающая тело человека для создания новых тел:
- 🤖 **Механических** (полностью роботизированные)
- 🦾 **Бионических** (гибриды человека и машины)
- 🧬 **Органических** (биоинженерные, генные)

## 🔄 Эволюционная прогрессия

Система проходит **11 этапов** последовательно — от механического к органическому:

### Этапы развития:

| Этап | Название | Описание |
|------|----------|----------|
| 1-3 | 🤖 Механическое | Изучение робототехники, протезов, материалов |
| 4-6 | 🦾 Бионическое | Гибридные технологии, нейроинтерфейсы, импланты |
| 7-9 | 🧬 Органическое | Биоинженерия, CRISPR, тканевая инженерия |
| 10-11 | ⚡ Синтез | Объединение всех технологий, финальная версия |

### Как работает:

1. **Начало** → Этап 1: `mechanical_research`
2. **Изучение тем** → Система учится из интернета
3. **Прогресс** → Автоматический переход при выполнении требований
4. **Эволюция** → Переход к следующему этапу
5. **Финал** → Полный цикл завершён

```
🤖 mechanical_research → mechanical_design → mechanical_complete
   ↓
🦾 bionic_research → bionic_design → bionic_complete
   ↓
🧬 organic_research → organic_design → organic_complete
   ↓
⚡ synthesis → final
```

## 📁 Структура

```
latislane/
├── __init__.py                 ← Пакет
├── latislane_core.py           ← Основное ядро (мозг системы)
├── body_modules.py             ← Модули тела (скелет, мышцы, нервы...)
├── internet_learning.py        ← Движок обучения из интернета
├── body_factory.py             ← Фабрика проектирования тел
└── DATA/
    ├── learning/               ← Данные обучения
    │   └── learning_state.json
    ├── bodies/                 ← Спецификации тел
    │   └── Mechanical-01.json
    └── system_state.json       ← Состояние системы
```

## 🚀 Быстрый старт

### 1. Инициализация

```python
from latislane import LatislaneCore

# Создание ядра
core = LatislaneCore(project_root=".", demo_mode=True)

# Изучение анатомии
core.start_anatomy_study()

# Цикл обучения
await core.run_study_cycle()
```

### 2. Проектирование тел

```python
# Механическое тело
mech_spec = core.design_mechanical_body(name="Mechanical-01")

# Бионическое тело
bionic_spec = core.design_bionic_body(name="Bionic-01")

# Органическое тело
organic_spec = core.design_organic_body(name="Organic-01")
```

### 3. Чат с Латислейн

```python
response = core.chat_response("какой прогресс изучения анатомии?")
print(response)
```

## 🌐 API Endpoints

Все эндпоинты доступны через `http://localhost:8000`

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/latislane/status` | GET | Статус системы |
| `/latislane/anatomy` | GET | Отчёт по анатомии |
| `/latislane/study` | POST | Запуск цикла обучения |
| `/latislane/design/mechanical` | POST | Проектирование механического тела |
| `/latislane/design/bionic` | POST | Проектирование бионического тела |
| `/latislane/design/organic` | POST | Проектирование органического тела |
| `/latislane/chat` | POST | Чат с системой |
| `/latislane/learn` | POST | Начать изучение анатомии |
| `/latislane/evolution` | GET | **Статус эволюции** |
| `/latislane/evolve` | POST | **Перейти к следующему этапу** |

### Примеры запросов

**Статус системы:**
```bash
curl http://localhost:8000/latislane/status
```

**Проектирование механического тела:**
```bash
curl -X POST http://localhost:8000/latislane/design/mechanical \
  -H "Content-Type: application/json" \
  -d '{"name": "Mechanical-X1"}'
```

**Чат с Латислейн:**
```bash
curl -X POST http://localhost:8000/latislane/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "какой прогресс изучения анатомии?"}'
```

**Статус эволюции:**
```bash
curl http://localhost:8000/latislane/evolution
```

**Переход к следующему этапу:**
```bash
curl -X POST http://localhost:8000/latislane/evolve
```

## 🧠 Модули тела

Система изучает 10 ключевых модулей:

| Модуль | Категория | Описание |
|--------|-----------|----------|
| `skeletal_system` | structural | Кости, суставы, хрящи |
| `muscular_system` | structural | Мышцы, сухожилия |
| `nervous_system` | nervous | Мозг, нервы, синапсы |
| `cardiovascular_system` | circulatory | Сердце, сосуды, кровь |
| `metabolic_system` | metabolic | Пищеварение, дыхание |
| `reproductive_system` | reproductive | Репродуктивные органы |
| `integumentary_system` | structural | Кожа, волосы, ногти |
| `endocrine_system` | metabolic | Гормоны, железы |
| `immune_system` | circulatory | Иммунитет, лейкоциты |
| `sensory_system` | nervous | Глаза, уши, нос, язык |

## 🎯 Типы тел

### Механическое (Mechanical)
- **Скелет:** титановые сплавы
- **Мышцы:** электроактивные полимеры
- **Нервная система:** нейроморфные чипы
- **Энергия:** литий-полимерные батареи

### Бионическое (Bionic)
- **Скелет:** углеродное волокно + титан
- **Мышцы:** 60% органических + 40% искусственных
- **Нервная система:** имплантируемые электроды
- **Органы:** гибридные (органические + искусственные)

### Органическое (Organic)
- **Все органы:** тканевая инженерия
- **Генетика:** CRISPR-Cas9 модификации
- **Рост:** 3D биопечать + stem-клетки
- **Иммунитет:** генно-модифицированный

## 🔗 Интеграция с Pantikur

Latislane интегрирован с чат-ботом Pantikur через `main.py`:

```python
# В main.py автоматически:
from latislane import LatislaneCore
latislane_core = LatislaneCore(project_root=str(BASE_DIR), demo_mode=True)
```

Бот может отвечать на вопросы о Латислейн через обычный чат.

## ⚙️ Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `LATISLANE_ENABLED` | Включить Latislane | `true` |
| `LATISLANE_DEMO_MODE` | Демо-режим (без реального веба) | `true` |

## 📊 Прогресс обучения

Система отслеживает прогресс по каждой теме:
- **0.0-0.3** — низкий (требует изучения)
- **0.3-0.6** — средний
- **0.6-0.9** — высокий
- **0.9-1.0** — отличный

## 🚀 Автономное обучение

```python
# Запуск непрерывного обучения
core.start_autonomous_learning(interval_minutes=10)
```

Система автоматически:
1. Определяет пробелы в знаниях
2. Ищет информацию в интернете
3. Извлекает ключевые знания
4. Обновляет спецификации тел

## 📝 Пример использования

```python
import asyncio
from latislane import LatislaneCore

async def main():
    # Инициализация
    core = LatislaneCore(demo_mode=True)
    
    # Изучение анатомии
    core.start_anatomy_study()
    await core.run_study_cycle()
    
    # Проектирование
    mech = core.design_mechanical_body("Robot-Alpha")
    bionic = core.design_bionic_body("Cyborg-Beta")
    organic = core.design_organic_body("Bio-Gamma")
    
    # Проверка статуса
    status = core.get_system_status()
    print(f"Прогресс: {status['learning_report']['overall_progress']*100:.1f}%")
    
    # Чат
    response = core.chat_response("расскажи о механических телах")
    print(response)

asyncio.run(main())
```

## 📚 Источники знаний (в режиме реального поиска)

В реальном режиме (не демо) система может использовать:
- **PubMed API** — медицинские статьи
- **Google Scholar** — научные публикации
- **arXiv** —预印本 по биоинженерии
- **GitHub** — открытые проекты робототехники

## 🛠️ Разработка

```bash
# Установка зависимостей
pip install torch fastapi uvicorn

# Запуск
python run.py
```

## 📄 Лицензия

MIT License — для исследовательских и образовательных целей.

---

**Latislane v0.1.0** — Изучаем тело. Создаём будущее. 🧬
