# 🌍 Модуль моделирования мировых состояний Футабы

## Обзор

Футаба теперь может **моделировать государства всех жанров и биомов** с инверсией правил от 0% до 100%, анализируя последствия для каждого сословия.

---

## Возможности

### 1. 📚 Жанры миров (10)

| Жанр | Описание | Уровень технологий |
|------|----------|-------------------|
| Фэнтези | Магия, мифические существа, средневековье | medieval |
| Научная фантастика | Космос, ИИ, футуризм | advanced |
| Киберпанк | Высокие технологии, корпорации | high_tech |
| Стимпанк | Паровые технологии, викторианская эпоха | industrial |
| Постапокалипсис | Мир после катастрофы | ruined |
| Исторический | Реальные исторические эпохи | historical |
| Антиутопия | Тоталитарное общество | modern_or_advanced |
| Утопия | Идеальное общество | advanced |
| Магическая академия | Школы магии | magical |
| Космическая опера | Галактические империи | space_age |

### 2. 🏛️ Биомы/Типы государств (17)

| Тип | Масштаб | Население | Управление |
|-----|---------|-----------|------------|
| Семья | micro | 5-50 | родители/старейшины |
| Клан/Род | micro | 50-500 | глава клана/совет |
| Племя | small | 500-5000 | вождь/совет вождей |
| Поселение/Деревня | small | 100-2000 | староста/совет |
| Город | medium | 2000-100000 | мэр/городской совет |
| Город-государство | medium | 50000-500000 | правитель/сенат |
| Княжество | medium | 100000-1000000 | князь/феодалы |
| Королевство | large | 1000000-10000000 | король/парламент |
| Империя | huge | 10000000+ | император/сенат |
| Республика | large | 1000000+ | президент/парламент |
| Федерация/Штаты | huge | 10000000+ | президент/конгресс |
| Конфедерация | huge | 10000000+ | совет представителей |
| Теократия | medium_to_large | 500000+ | верховный жрец/совет |
| Магократия | medium_to_large | 500000+ | архимаг/совет магов |
| Корпоратократия | large | 1000000+ | CEO/совет директоров |
| Коммуна/Община | small | 100-1000 | общее собрание |
| Коллективный разум | any | variable | коллективное решение |

### 3. ⚖️ Правила государства (25)

**Фундаментальные (fundamental):**
1. Право на жизнь
2. Право на свободу
3. Право на собственность
4. Равенство перед законом
5. Свобода слова
6. Свобода совести
16. Неприкосновенность жилища
17. Тайна переписки
19. Запрет пыток
20. Запрет рабства

**Социальные (social):**
7. Право на образование
8. Право на труд
9. Право на отдых
10. Право на здравоохранение
11. Социальная защита

**Политические (political):**
12. Избирательное право
13. Право на участие в управлении
14. Свобода собраний
15. Свобода объединений

**Юридические (legal):**
18. Презумпция невиновности

**Экономические (economic):**
21. Свобода предпринимательства
22. Защита конкуренции
23. Право на справедливые налоги

**Экологические (environmental):**
24. Экологическая защита

**Культурные (cultural):**
25. Защита культурного наследия

---

## Типы моделирования

### 1. Идеальное государство (0% инверсии)

```python
result = modeler.simulate_ideal_state("fantasy", "kingdom")
# {
#   "overall_score": 0.575,
#   "stability_score": 0.500,
#   "justice_score": 0.650,
#   "recommendation": "Рекомендуется постепенная реформа."
# }
```

### 2. Инверсия 1 правила

```python
result = modeler.simulate_single_inversion("fantasy", "kingdom", rule_id=1)
# Инверсия: "НЕ (Право на жизнь)"
# overall_score: 0.461 (снижение на 19.8%)
```

### 3. Инверсия 2 правил

```python
result = modeler.simulate_double_inversion("fantasy", "kingdom", [1, 2])
# Инверсия: ["НЕ (Право на жизнь)", "НЕ (Право на свободу)"]
# overall_score: 0.348 (снижение на 39.5%)
```

### 4. Прогрессивная инверсия (0% → 100%)

```python
results = modeler.simulate_progressive_inversion(
    "fantasy", "kingdom", max_percentage=100
)
# Возвращает список результатов для каждого уровня инверсии
```

**Пример результатов:**
```
Level | Percent | Score   | Status
------|---------|---------|------------------
    0 |    0.0% | 0.575   | Идеальное состояние
    5 |   20.0% | 0.150   | КРИТИЧЕСКИ: Требуется стабилизация
   10 |   40.0% | 0.150   | КРИТИЧЕСКИ: Требуется стабилизация
   15 |   60.0% | 0.100   | Полный коллапс
   20 |   80.0% | 0.050   | Полный коллапс
   25 |  100.0% | 0.000   | Апокалипсис
```

---

## Расчёт показателей

### Score для каждого сословия

```python
base_score = 0.5
inverted_penalty = len(inverted_rules) * 0.1
removed_penalty = len(removed_rules) * 0.08

# Уязвимые страдают больше
if estate == "vulnerable":
    inverted_penalty *= 1.5
    removed_penalty *= 1.5

# Модификатор жанра
if genre == "dystopia":
    genre_modifier = -0.2
elif genre == "utopia":
    genre_modifier = 0.2

# Финальный score
final_score = max(0, min(1, base_score - inverted_penalty - removed_penalty + genre_modifier))
```

### Статусы

| Score | Статус |
|-------|--------|
| ≥ 0.8 | prosperous |
| ≥ 0.6 | stable |
| ≥ 0.4 | unstable |
| ≥ 0.2 | critical |
| < 0.2 | collapse |

### Stability Score

```python
avg_score = sum(estate_scores) / len(estate_scores)
variance = sum((s - avg) ** 2 for s in estate_scores) / len(estate_scores)
inequality_penalty = min(0.3, variance * 0.5)
stability = max(0, min(1, avg_score - inequality_penalty))
```

### Justice Score

```python
min_score = min(estate_scores)
avg_score = sum(estate_scores) / len(estate_scores)
max_score = max(estate_scores)
gap = max_score - min_score

justice = min_score * 0.7 + (1 - gap) * 0.3
```

---

## Интеграция с ядром Футабы

### Инициализация

```python
from futaba.engine.futaba_core import FutabaCore
from futaba.engine.config import FutabaConfig

config = FutabaConfig.default()
core = FutabaCore(config)

# world_modeler уже инициализирован
# core.world_modeler = FutabaWorldStateModeler(config)
```

### Автономный цикл

```
ЦИКЛ МОДЕЛИРОВАНИЯ (каждые 10 циклов):
  1. 🏛️ Моделирование идеальных государств
  2. 🔄 Инверсия 1 правила
  3. 🔄🔄 Инверсия 2 правил
  4. 📈 Прогрессивная инверсия
  5. 📊 Статистика
```

### Метрики

```python
core.metrics = {
    "world_simulations_run": 0,
    "ideal_states_modeled": 0,
    ...
}
```

---

## Примеры использования

### Получить все жанры

```python
from futaba.engine.world_state_modeler import FutabaWorldStateModeler
from futaba.engine.config import FutabaConfig

modeler = FutabaWorldStateModeler(FutabaConfig.default())

genres = modeler.get_all_world_genres()
# 10 жанров
```

### Получить все биомы

```python
biomes = modeler.get_all_state_biomes()
# 17 типов государств
```

### Получить все правила

```python
rules = modeler.get_state_rules()
# 25 правил
```

### Смоделировать идеальное государство

```python
ideal = modeler.simulate_ideal_state("cyberpunk", "corporatocracy")
print(f"Score: {ideal['overall_score']:.3f}")
print(f"Stability: {ideal['stability_score']:.3f}")
print(f"Justice: {ideal['justice_score']:.3f}")
```

### Прогрессивная инверсия

```python
results = modeler.simulate_progressive_inversion(
    genre="scifi",
    biome="empire",
    max_percentage=100
)

for result in results:
    print(f"{result['inversion_percentage']:.1f}%: "
          f"Score={result['overall_score']:.3f}")
```

### Статистика

```python
stats = modeler.get_simulation_statistics()
# {
#   "total_simulations": 19,
#   "average_score": 0.303,
#   "by_genre": {"Фэнтези": 19},
#   "by_simulation_type": {...}
# }
```

### Экспорт результатов

```python
filepath = modeler.export_results("my_simulation.json")
# Сохраняет в futaba/engine/state/my_simulation.json
```

---

## Архитектура

```
futaba/engine/
├── world_state_modeler.py    # Модуль моделирования
├── futaba_core.py            # Ядро с интеграцией
└── state/
    ├── world_simulation_cache.json      # Кэш
    └── world_simulation_results.json    # Результаты
```

---

## Влияние инверсии правил

### 0% инверсии (Идеальное)
- **Score:** 0.575
- **Статус:** stable
- **Рекомендация:** Постепенная реформа

### 20% инверсии (5 правил)
- **Score:** 0.150
- **Статус:** critical
- **Рекомендация:** КРИТИЧЕСКИ: Требуется стабилизация

### 40% инверсии (10 правил)
- **Score:** 0.100
- **Статус:** collapse
- **Рекомендация:** Полный коллапс системы

### 100% инверсии (25 правил)
- **Score:** 0.000
- **Статус:** apocalypse
- **Рекомендация:** Апокалипсис, полное уничтожение

---

## Сословия и влияние

Для каждого сословия рассчитывается влияние:

1. **Граждане (все)** — базовые права
2. **Предприниматели** — экономические права
3. **Работники** — социальные права
4. **Фермеры** — земельные права
5. **Гос. служащие** — административные права
6. **Уязвимые** — специальная защита (страдают больше всех)
7. **Учёные** — интеллектуальные права

**Формула:**
- Уязвимые получают x1.5 штраф за инверсию/удаление прав
- Малые сообщества (micro, small) более устойчивы (+0.1)
- Крупные империи менее устойчивы (-0.05)
- Жанр влияет: dystopia -0.2, utopia +0.2, postapoc -0.15

---

## Статистика моделирования

На момент интеграции:
- **Жанров:** 10
- **Биомов:** 17
- **Правил:** 25
- **Проведено симуляций:** 19+
- **Средний Score:** 0.303

---

## Команды для запуска

```bash
# Запуск Футабы с моделированием
python -m futaba.engine.run --demo

# Проверка статуса
python -m futaba.engine.run --status

# Моделирование вручную
python -c "
from futaba.engine.world_state_modeler import FutabaWorldStateModeler
from futaba.engine.config import FutabaConfig
m = FutabaWorldStateModeler(FutabaConfig.default())
ideal = m.simulate_ideal_state('fantasy', 'kingdom')
print(f'Ideal Score: {ideal[\"overall_score\"]:.3f}')
"
```

---

## Заключение

Теперь Футаба может:
1. ✅ Моделировать государства всех жанров (10)
2. ✅ Анализировать все типы государств (17)
3. ✅ Работать со всеми правилами (25)
4. ✅ Инвертировать правила (0% → 100%)
5. ✅ Оценивать последствия для 7 сословий
6. ✅ Рассчитывать stability и justice scores
7. ✅ Генерировать рекомендации
8. ✅ Интегрирована с автономным циклом

**Футаба теперь может моделировать идеальные и катастрофические государства для всех миров!** 🌍⚖️

---

*Футаба — Управление, Нобука — Улучшения, Шиори — Защита*  
*World State Modeler v1.0.0 | Статус: ✅ Активен*
