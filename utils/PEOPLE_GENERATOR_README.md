# People Generator — Генератор людей, семей, организаций и стран

## 📋 Описание

Скрипт `utils/world_people_generator.py` генерирует психологически достоверных персонажей, семьи, организации и страны на основе **8 файлов знаний**:

- `human_adolescence.md` — подростковый возраст
- `human_early_development.md` — раннее развитие
- `human_emerging_adulthood.md` — ранняя взрослость (19–23 года)
- `human_late_adolescence.md` — поздний подростковый возраст
- `human_middle_childhood.md` — среднее детство
- `human_24_years.md` — 24 года (детальный профиль)
- `human_daily_life.md` — повседневная жизнь
- `human_daily_routine.md` — рутина, работа, выходные, отпуск

## 🔧 Установка

Никаких дополнительных зависимостей не требуется. Скрипт использует стандартные библиотеки Python.

## 📖 Использование

### 1. Генерация через CLI

```bash
# Сгенерировать популяцию мира
python utils/world_people_generator.py --people 50 --families 10 --organizations 5 --countries 3

# С параметрами
python utils/world_people_generator.py --people 100 --families 20 --organizations 10 --countries 5 --knowledge-dir data/knowledge

# Добавить людей в существующий мир
python utils/world_people_generator.py --add-to-world "НазваниеМира" --people 20
```

### 2. Генерация через Python API

```python
from utils.world_people_generator import PeopleGenerator

# Инициализация
generator = PeopleGenerator(knowledge_dir="data/knowledge")

# Сгенерировать человека
person = generator.generate_person(
    age_range=(20, 30),
    gender="мужской",  # или "женский"
    archetype="Выпускник-достигатор"  # опционально
)
print(person.to_dict())

# Сгенерировать семью
family = generator.generate_family(size=4, region="Москва")
print(family.to_dict())

# Сгенерировать организацию
org = generator.generate_organization(type="company", size="medium")
print(org.to_dict())

# Сгенерировать страну
country = generator.generate_country(population_range=(1000000, 50000000))
print(country.to_dict())

# Сгенерировать полную популяцию мира
world_data = generator.generate_world_population(
    num_people=100,
    num_families=20,
    num_organizations=10,
    num_countries=5
)
```

### 3. Генерация через REST API

```bash
# Сгенерировать человека
curl -X POST http://localhost:8000/generate/person \
  -H "Content-Type: application/json" \
  -d '{"age_min": 20, "age_max": 30, "gender": "мужской"}'

# Сгенерировать семью
curl -X POST http://localhost:8000/generate/family \
  -H "Content-Type: application/json" \
  -d '{"size": 4, "region": "Москва"}'

# Сгенерировать организацию
curl -X POST http://localhost:8000/generate/organization \
  -H "Content-Type: application/json" \
  -d '{"type": "company", "size": "medium"}'

# Сгенерировать страну
curl -X POST http://localhost:8000/generate/country \
  -H "Content-Type: application/json" \
  -d '{"population_min": 1000000, "population_max": 50000000}'

# Сгенерировать популяцию мира
curl -X POST http://localhost:8000/generate/world-population \
  -H "Content-Type: application/json" \
  -d '{"people": 50, "families": 10, "organizations": 5, "countries": 3}'

# Добавить людей в существующий мир
curl -X POST http://localhost:8000/world/НазваниеМира/add-people \
  -H "Content-Type: application/json" \
  -d '{"num": 20}'
```

## 📊 Структура данных

### Person (Человек)

```json
{
  "id": "abc123",
  "name": "Александр Иванов",
  "age": 24,
  "gender": "мужской",
  "archetype": "Выпускник-достигатор",
  "education": "Высшее",
  "job": "Программист",
  "finance": "Средний класс",
  "housing": "Квартира",
  "relationships": "В отношениях",
  "children": "Нет детей",
  "region": "Москва",
  "temperament": "Сангвиник",
  "sociality": "Амбиверт",
  "routine_type": "Стандартная",
  "weekend_type": "Активные",
  "parenting_style": "Авторитетный",
  "vacation_type": "Пляжный",
  "health": "Хорошее",
  "values": ["Семья", "Карьера", "Развитие"],
  "habits": ["Чтение", "Спорт", "Кофе"],
  "goals": ["Развитие", "Путешествия"],
  "problems": ["Усталость", "Стресс"],
  "created_at": "2025-01-15T10:30:00"
}
```

### Family (Семья)

```json
{
  "id": "fam123",
  "name": "Семья Ивановых",
  "members": [...],
  "relationships": {...},
  "traditions": ["Совместный ужин", "Поездки на дачу"],
  "problems": ["Баланс работа-семья"],
  "budget": "средний",
  "housing": "квартира",
  "region": "Москва",
  "created_at": "2025-01-15T10:30:00"
}
```

### Organization (Организация)

```json
{
  "id": "org123",
  "name": "ООО \"ТехноГрупп\"",
  "type": "company",
  "size": "medium",
  "industry": "IT",
  "culture": "Корпоративная",
  "goals": ["Рост прибыли", "Развитие"],
  "members": [],
  "resources": {"money": 500000, "reputation": 0.8, "influence": 0.6},
  "reputation": 0.8,
  "created_at": "2025-01-15T10:30:00"
}
```

### Country (Страна)

```json
{
  "id": "country123",
  "name": "Россия",
  "population": 146000000,
  "gdp_per_capita": 12000.5,
  "government_type": "Республика",
  "culture": "Смешанная",
  "regions": ["Московская область", "Ленинградская область"],
  "cities": ["Москва", "Санкт-Петербург"],
  "laws": ["Конституция", "Налоговый кодекс"],
  "traditions": ["Новый год", "День Победы"],
  "created_at": "2025-01-15T10:30:00"
}
```

## 🧩 Интеграция с WorldEngine

```python
from utils.world_people_generator import WorldEngineIntegration

# Инициализация
integration = WorldEngineIntegration()

# Добавить 20 персонажей в существующий мир
success = integration.add_people_to_world("НазваниеМира", num_people=20)

if success:
    print("✅ Персонажи добавлены в мир")
else:
    print("❌ Ошибка добавления")
```

## 📁 Выходные файлы

Все сгенерированные данные сохраняются в:
```
data/generated_worlds/world_population_YYYYMMDD_HHMMSS.json
```

Файл содержит:
- `people` — список людей
- `families` — список семей
- `organizations` — список организаций
- `countries` — список стран
- `stats` — статистика по популяции

## 🎯 Параметры генерации

### Человек
- `age_range` — диапазон возраста (по умолчанию: 18–40)
- `gender` — пол ("мужской" / "женский")
- `archetype` — архетип личности

### Семья
- `size` — количество членов семьи (по умолчанию: 4)
- `region` — регион проживания

### Организация
- `type` — тип (company, government, ngo, club, criminal)
- `size` — размер (small, medium, large, corporation)

### Страна
- `population_range` — диапазон населения (по умолчанию: 1M–100M)

## 📝 Примеры использования

### Генерация реалистичного персонажа

```python
generator = PeopleGenerator()

# Молодой специалист в Москве
person = generator.generate_person(
    age_range=(22, 26),
    gender="мужской",
    archetype="Выпускник-достигатор"
)

# Опытная мать в регионе
mother = generator.generate_person(
    age_range=(35, 45),
    gender="женский",
    archetype="Молодой родитель"
)
```

### Генерация полноценного мира

```python
world_data = generator.generate_world_population(
    num_people=500,        # 500 человек
    num_families=100,      # 100 семей
    num_organizations=25,  # 25 организаций
    num_countries=7        # 7 стран
)

print(f"Сгенерировано:")
print(f"  Людей: {world_data['stats']['total_people']}")
print(f"  Семей: {world_data['stats']['total_families']}")
print(f"  Организаций: {world_data['stats']['total_organizations']}")
print(f"  Стран: {world_data['stats']['total_countries']}")
```

## 🔍 Парсинг знаний

Скрипт автоматически парсит markdown-таблицы из файлов знаний для извлечения:
- Архетипов личности
- Типов образования
- Профессий и работ
- Финансовых статусов
- Типов жилья
- Отношений и детей
- Регионов
- Темпераментов
- Типов рутины и выходных
- Стилей воспитания
- Типов отпуска
- Ценностей и привычек
- Целей и проблем

## ⚙️ Конфигурация

```python
# В начале скрипта
DEFAULT_KNOWLEDGE_DIR = "data/knowledge"  # Директория с знаниями
DEFAULT_OUTPUT_DIR = "data/generated_worlds"  # Директория для вывода

KNOWLEDGE_FILES = [
    "human_adolescence.md",
    "human_early_development.md",
    "human_emerging_adulthood.md",
    "human_late_adolescence.md",
    "human_middle_childhood.md",
    "human_24_years.md",
    "human_daily_life.md",
    "human_daily_routine.md",
]
```

## 🚀 Производительность

- Генерация 1 человека: ~10–50 мс
- Генерация 1 семьи: ~50–100 мс
- Генерация 1 организации: ~10–30 мс
- Генерация 1 страны: ~10–30 мс
- Генерация популяции (50 человек + 10 семей + 5 организаций + 3 страны): ~500–1000 мс

## 📚 Зависимости

- Python 3.9+
- Стандартные библиотеки: `os`, `re`, `json`, `random`, `hashlib`, `datetime`, `pathlib`, `dataclasses`

## 🛠 Отладка

```python
# Включить подробное логирование
import logging
logging.basicConfig(level=logging.DEBUG)

# Проверить загрузку знаний
generator = PeopleGenerator()
print(generator.knowledge_data.keys())

# Проверить распарсенные параметры
options = generator.parser.get_parameter_options("архетип")
print(f"Доступные архетипы: {options}")
```

## 📞 API Endpoints

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/generate/person` | POST | Сгенерировать человека |
| `/generate/family` | POST | Сгенерировать семью |
| `/generate/organization` | POST | Сгенерировать организацию |
| `/generate/country` | POST | Сгенерировать страну |
| `/generate/world-population` | POST | Сгенерировать популяцию мира |
| `/world/{name}/add-people` | POST | Добавить людей в мир |

## 🎨 Примеры ответов API

См. раздел "Структура данных" выше для примеров JSON-ответов.

---

**Создано для:** Pantikur ChatBot  
**Версия:** 1.0  
**Дата:** 2025-01-15
