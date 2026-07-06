# Использование японских имён в генераторе миров

## 📋 Обзор

Файл `data/knowledge/japanese_names_complete.md` содержит **5000+ японских имён и названий**, интегрированных в систему генерации миров Pantikur ChatBot.

## 📊 Содержание файла

| Категория | Количество | Примеры |
|-----------|-----------|---------|
| Женские имена | 1500+ | Аой, Сакура, Футаба, Шиори, Мидори |
| Мужские имена | 1200+ | Акира, Кэндзи, Рю, Такуми, Хироси |
| Фамилии | 800+ | Танака, Сузуки, Сато, Ватанабэ, Кимура |
| Города и места | 500+ | Токио, Киото, Осака, Канагава, Иватэ |
| Клановые названия | 300+ | Фудзивара, Токугава, Такеда |
| Поэтические названия | 400+ | Асагири, Кокоро, Юмэ, Хикари |
| Храмы и святилища | 200+ | Хасэдэра, Токидзи, Киёмидзу |
| Титулы и звания | 100+ | Тэнно, Сёгун, Самурай |

## 🚀 Использование

### Через CLI (командную строку)

```powershell
# Генерация популяции с японскими именами
python utils/world_people_generator.py --people 50 --families 10 --japanese-names

# Генерация без японских имён (по умолчанию)
python utils/world_people_generator.py --people 50 --families 10
```

### Через Python API

```python
from utils.world_people_generator import PeopleGenerator

# Инициализация генератора
generator = PeopleGenerator(knowledge_dir="data/knowledge")

# Генерация одного персонажа с японским именем
person = generator.generate_person(
    age_range=(20, 35),
    gender="женский",  # или "мужской"
    use_japanese_names=True
)
print(person.name)  # Например: "Сакура Танака"

# Генерация семьи с японскими именами
family = generator.generate_family(
    size=4,
    use_japanese_names=True
)
print(family.name)  # Например: "Семья Танакаых"
print(family.region)  # Например: "Киото"

# Генерация полной популяции мира
world_data = generator.generate_world_population(
    num_people=100,
    num_families=20,
    num_organizations=10,
    num_countries=5,
    use_japanese_names=True
)
```

### Интеграция с WorldEngine

```python
from utils.world_people_generator import WorldEngineIntegration

# Добавление персонажей с японскими именами в существующий мир
integration = WorldEngineIntegration()
integration.add_people_to_world("my_world_name", num_people=20)
```

## 📝 Формат имён

Японские имена генерируются в формате:
```
{Фамилия} {Имя}
```

Примеры:
- **Танака Юки** (женское)
- **Сузуки Кэндзи** (мужское)
- **Ватанабэ Сакура** (женское)

## 🏙️ Японские локации

При использовании `use_japanese_names=True` регионы генерируются из японских названий:
- Токио
- Киото
- Осака
- Канагава
- Иватэ
- Хоккайдо
- Фукуока
- Нагасаки
- И многие другие (108 локаций)

## 🎯 Примеры использования

### Создание японского города

```python
# Генерация 100 жителей японского города
generator = PeopleGenerator()
world = generator.generate_world_population(
    num_people=100,
    num_families=25,
    use_japanese_names=True
)

# Сохранение в файл
import json
with open('data/generated_worlds/japanese_city.json', 'w', encoding='utf-8') as f:
    json.dump(world, f, ensure_ascii=False, indent=2)
```

### Смешанная популяция

```python
# 50% персонажей с японскими именами, 50% с русскими
people = []
for i in range(50):
    person = generator.generate_person(use_japanese_names=(i % 2 == 0))
    people.append(person)
```

## 🔧 Настройки

### Кодировка

Скрипт автоматически определяет платформу и устанавливает UTF-8 кодировку для Windows:

```python
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
```

### Кэширование

Японские имена загружаются один раз при инициализации генератора и кэшируются в памяти:
- `self.japanese_names_female` — список женских имён
- `self.japanese_names_male` — список мужских имён
- `self.japanese_surnames` — список фамилий
- `self.japanese_locations` — список локаций

## 📈 Статистика загрузки

При запуске скрипт выводит информацию о загруженных именах:

```
✅ Загружено японских имён: женских=1431, мужских=633, фамилий=648, локаций=108
```

## ⚠️ Примечания

1. **Кодировка**: Все файлы используют UTF-8 для корректного отображения кириллицы
2. **Формат**: Имена записаны кириллицей (без кандзи) для совместимости
3. **Порядок**: Фамилия указывается перед именем (японский стиль)
4. **Регионы**: При использовании японских имён регионы выбираются из японских городов/префектур

## 📚 Дополнительные файлы

- `data/knowledge/japanese_names_complete.md` — основной справочник имён
- `utils/world_people_generator.py` — генератор с поддержкой японских имён
- `data/generated_worlds/` — папка для сгенерированных миров

## 🎌 Примеры сгенерированных имён

### Женские
- Аой Танака
- Сакура Сузуки
- Мидори Ватанабэ
- Футаба Като
- Шиори Ёсида

### Мужские
- Акира Сато
- Кэндзи Танака
- Рю Ямамото
- Такуми Накамура
- Хироси Кобаяси

---

**Версия:** 1.0  
**Дата:** 2026-01-15  
**Интеграция:** Pantikur ChatBot World Generation System
