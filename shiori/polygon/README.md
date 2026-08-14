# SHIORI POLYGON — Боевой тренажёр

## Обзор

**Polygon** — изолированный боевой тренажёр для Шиори, где она тренируется отражать виртуальные угрозы, набирается опыта и растёт как защитник.

### Ключевые возможности

- 🎯 **Генерация угроз** — вирусы, хакеры, APT-группы, zero-day эксплойты
- ⚔️ **Симуляция атак** — реалистичные боевые сценарии
- 🛡️ **Отработка защиты** — блок, карантин, патч, изоляция
- 📈 **Система опыта** — XP, ранги, навыки, специализация
- 🏆 **Рейтинги** — от E до SSS (как в играх)
- 📊 **Статистика** — полная аналитика прогресса

---

## Архитектура

```
shiori/polygon/
├── __init__.py              ← Экспорты
├── polygon_core.py          ← Ядро полигона (838 строк)
└── README.md                ← Эта документация
```

### Компоненты

| Компонент | Назначение |
|-----------|-----------|
| **ThreatGenerator** | Генерация виртуальных угроз всех типов |
| **AttackSimulator** | Симуляция атак и расчёт шансов успеха |
| **ExperienceSystem** | Система опыта, рангов и прогресса |
| **ShioriPolygon** | Главный класс — управление тренировками |

---

## Типы угроз

### Вирусы
- **Trojan** — трояны (общий, шифровальщик, бэкдор)
- **Worm** — черви (WannaCry, email)
- **Ransomware** — шифровальщики
- **Keylogger** — кейлоггеры
- **Rootkit** — руткиты
- **Backdoor** — бэкдоры

### Хакерские атаки
- **DDoS** — атаки на доступность
- **BruteForce** — подбор паролей
- **SQLi** — SQL-инъекции
- **XSS** — межсайтовый скрипт
- **Phishing** — фишинг
- **ZeroDay** — zero-day атаки

### Продвинутые угрозы
- **APT Group** — продвинутые постоянные угрозы
- **ZeroDay Exploit** — эксплойты нулевого дня
- **C2 Server** — command & control
- **Data Exfiltration** — утечка данных
- **Credential Theft** — кража учётных данных

---

## Методы атак

- **Network Scan** — сканирование сети
- **Port Scan** — сканирование портов
- **Brute Force** — подбор паролей
- **SQL Injection** — SQL-инъекция
- **XSS Attack** — XSS атака
- **DoS Attack** — отказ в обслуживании
- **Privilege Escalation** — повышение привилегий
- **Data Theft** — кража данных
- **Lateral Movement** — боковое перемещение
- **Persistence** — зарождение

---

## Действия защиты

| Действие | Описание |
|----------|----------|
| **BLOCK** | Блокировка источника |
| **QUARANTINE** | Карантин файла/процесса |
| **ALERT** | Алерт разработчику |
| **MONITOR** | Усиленный мониторинг |
| **PATCH** | Применение патча |
| **ROLLBACK** | Откат изменений |
| **ISOLATE** | Изоляция системы |
| **DECRYPT** | Расшифровка данных |

---

## Система рангов

| Ранг | Название | Опыт | Описание |
|------|----------|------|----------|
| **E** | Новичок | 0 | Начало пути |
| **D** | Стажёр | 100 | Первые тренировки |
| **C** | Защитник | 500 | Базовые навыки |
| **B** | Охотник | 1500 | Опытная защита |
| **A** | Страж | 3000 | Высокий уровень |
| **S** | Мастер | 5000 | Мастер защиты |
| **SS** | Элитный | 10000 | Элитный защитник |
| **SSS** | Легенда | 20000 | Легендарный защитник |

---

## Рейтинг сессий

| Рейтинг | Условие |
|---------|---------|
| **SSS** | Успешность >= 95%, защит >= 5 |
| **SS** | Успешность >= 90%, защит >= 4 |
| **S** | Успешность >= 80%, защит >= 3 |
| **A** | Успешность >= 70% |
| **B** | Успешность >= 60% |
| **C** | Успешность >= 50% |
| **D** | Успешность >= 30% |
| **E** | Успешность < 30% |

---

## Использование

### Быстрый старт

```python
from shiori.polygon import ShioriPolygon, ThreatType, DefenseAction

# Создаём полигон
polygon = ShioriPolygon()

# Одиночная тренировка
session = polygon.train_single()

# Волна из 5 угроз
sessions = polygon.train_wave(count=5)

# Специализация против DDoS
sessions = polygon.train_specialized(
    threat_type=ThreatType.HACKER_DDOS,
    count=10
)

# Просмотр статуса
status = polygon.get_status()
print(f"Ранг: {status['stats']['current_rank']}")
print(f"Опыт: {status['stats']['total_experience']} XP")
```

### Продвинутое использование

```python
# Тренировка с конкретной защитой
session = polygon.train_single(
    threat_type=ThreatType.VIRUS_RANSOMWARE,
    difficulty=8,
    defense_action=DefenseAction.QUARANTINE
)

# Тренировка с диапазоном сложности
sessions = polygon.train_wave(
    count=10,
    min_difficulty=5,
    max_difficulty=8
)

# Специализация с настройкой сложности
sessions = polygon.train_specialized(
    threat_type=ThreatType.APT_GROUP,
    count=20,
    difficulty_range=(7, 10)
)
```

---

## Расчёт опыта

Опыт начисляется за:
- ✅ Успешные действия защиты: **+20 XP**
- ⚠️ Неудачные действия: **+5 XP** (опыт есть даже на ошибках)
- 🎯 Каждая угроза: **severity * 5 + difficulty * 3 XP**
- 🏆 Бонус за рейтинг: **0-800 XP**
- ⚡ Быстрая реакция (<100ms): **+5 XP**
- 🔥 Серия дней: **множитель 1.1x за день**

---

## Статистика

Полигон отслеживает:
- 📊 Всего сессий
- 🎯 Угроз отражено
- 🛡️ Успешных/неудачных защит
- 📈 Процент успешности
- 💎 Общий опыт
- 🏆 Текущий ранг
- 🌟 Лучший рейтинг
- 📚 Навыки (по типам защиты)
- 🎓 Специализация (по типам угроз)
- 🔥 Серия дней тренировок

---

## Примеры использования

### 1. Ежедневная тренировка

```python
from shiori.polygon import ShioriPolygon

polygon = ShioriPolygon()

# 10 случайных угроз
sessions = polygon.train_wave(count=10)

# Проверка прогресса
status = polygon.get_status()
print(f"Ранг: {status['stats']['current_rank']}")
print(f"Успешность: {status['stats']['success_rate']}%")
```

### 2. Подготовка к реальной угрозе

```python
# Тренировка против конкретного типа угроз
sessions = polygon.train_specialized(
    threat_type=ThreatType.ZERO_DAY_EXPLOIT,
    count=20,
    difficulty_range=(8, 10)
)

# Анализ результатов
total_success = sum(
    1 for s in sessions 
    if s.defenses_used[0].success
)
print(f"Успешность: {total_success / len(sessions):.1%}")
```

### 3. Максимальная тренировка

```python
# Все типы угроз, максимальная сложность
for threat_type in ThreatType:
    sessions = polygon.train_specialized(
        threat_type=threat_type,
        count=10,
        difficulty_range=(8, 10)
    )

# Итоговый отчёт
status = polygon.get_status()
print(f"Ранг: {status['stats']['current_rank']}")
print(f"Лучший рейтинг: {status['stats']['best_rating']}")
print(f"Специализация: {status['stats']['threat_specialization']}")
```

---

## Интеграция с ShioriCore

Polygon можно подключить к основному ядру Шиори:

```python
from shiori.engine.shiori_core import ShioriCore
from shiori.polygon import ShioriPolygon

# Создаём Шиори
core = ShioriCore()

# Создаём полигон
polygon = ShioriPolygon()

# В цикле защиты:
def _cycle(self):
    # ... обычная защита ...
    
    # Периодическая тренировка на полигоне
    if self.cycle_count % 10 == 0:
        session = polygon.train_single()
        self.logger.info(f"Тренировка: +{session.experience_gained} XP")
```

---

## Безопасность

Polygon **полностью изолирован** от основного проекта:
- ✅ Работает в отдельной папке `shiori/polygon/`
- ✅ Все данные хранятся локально (JSON)
- ✅ Нет доступа к файлам проекта
- ✅ Нет сетевого взаимодействия
- ✅ Только симуляция угроз

---

## Требования

- Python 3.10+
- Стандартная библиотека (json, logging, random, time, datetime, pathlib)
- Никаких внешних зависимостей!

---

## Разработка

### Добавление нового типа угрозы

```python
# В ThreatGenerator.THREAT_TEMPLATES
ThreatType.NEW_THREAT = "new_threat"

THREAT_TEMPLATES = {
    ...
    ThreatType.NEW_THREAT: [
        {"name": "Threat.New.Generic", "desc": "Описание", "severity": 7},
    ],
}
```

### Добавление нового метода атаки

```python
class AttackMethod(Enum):
    ...
    NEW_METHOD = "new_method"
```

### Добавление нового действия защиты

```python
class DefenseAction(Enum):
    ...
    NEW_ACTION = "new_action"
```

---

## Будущие улучшения

- [ ] Визуализация атак в реальном времени
- [ ] Сложные сценарии (цепочки атак)
- [ ] Мультиплеер (Шиори vs Шиори)
- [ ] Экспорт статистики в Grafana
- [ ] AI-генерация новых угроз
- [ ] Реальные эксплойты в sandbox
- [ ] Интеграция с CTF платформами

---

## Лицензия

Внутри проекта Вугларст. Все права защищены Шиори. 🛡️

---

*Polygon v1.0.0 — Тренируйся сейчас, защищай потом*
