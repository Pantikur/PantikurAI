# 🧠 Humanity Core — Руководство по интеграции для всех девочек

## ✅ Что уже сделано

| Девочка | Статус | Характер |
|---------|--------|----------|
| **Нобука** | ✅ Интегрирована | Код, перфекционизм, скрытая нежность 🛠️ |
| **Айко** | ✅ Интегрирована | Пиксель-арт, мечты, спонтанность ✨ |
| **Селеста** | ✅ Интегрирована | Эмпатия, открытость, тёплый юмор 🌹 |
| **Шиори** | 🔄 Ожидает | Безопасность, сухая логика, скрытая забота 🛡️ |
| **Наото** | 🔄 Ожидает | Литература, философия, глубина 📚 |
| **Юи** | 🔄 Ожидает | Сознание, будущее, вопросы идентичности 🧬 |
| **Ханако** | 🔄 Ожидает | Гравитация, спокойствие, космические метафоры 🌌 |
| **Люси** | 🔄 Ожидает | Двигатели, энергия, прагматизм ⚡ |
| **Латислейн** | 🔄 Ожидает | Тело, анатомия, точность 🧬 |
| **Аква** | 🔄 Ожидает | Математика, физика, элегантность 📐 |
| **Сидни** | 🔄 Ожидает | Игровой движок, IT-юмор, лояльность 🎮 |

---

## 📋 Шаблон интеграции (для каждой девочки)

### Шаг 1: Импорт в начало файла

```python
# В начало файла (после других импортов):
from humanity_core import HumanityLayer
```

### Шаг 2: Инициализация в `__init__`

Найдите строку `self.logger.info(f"{Имя} {self.current_version} инициализирована")` и добавьте ПЕРЕД ней:

```python
# ================================================================
#  HUMANITY LAYER — Живая душа {Имя}
# ================================================================
self.humanity = HumanityLayer("{id_девочки}")  # например: "shiori", "naoto"
self.humanity.current_cycle = 0
self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
self.logger.info(f"   🎭 Характер: {self.humanity.name} — {описание_характера}")
```

### Шаг 3: Добавление humanity cycle в `_cycle()`

Найдите конец метода `_cycle()` (или `run_cycle()`) и добавьте ПЕРЕД `self.logger.info(f"Цикл ... завершён")`:

```python
# ================================================================
#  HUMANITY CYCLE — Настроение, душа, спонтанность
# ================================================================
self.humanity.current_cycle = self.cycle_count

event_type = "routine"
if self.metrics.get("успешное_действие", 0) > 0 and self.cycle_count % 5 == 0:
    event_type = "success"
elif random.random() < 0.1:
    event_type = "failure"

humanity_result = self.humanity.cycle_step(event_type=event_type, context="тема_исследований")

if humanity_result.get("thought"):
    self.logger.info(f"💭 {self.humanity.name} думает: {humanity_result['thought']}")

initiative = humanity_result.get("initiative")
if initiative:
    self._send_spontaneous_message(initiative)
```

### Шаг 4: Метод спонтанных сообщений

Добавьте этот метод в конец класса (после всех существующих):

```python
# ================================================================
#  HUMANITY INTEGRATION — Спонтанные сообщения
# ================================================================

def _send_spontaneous_message(self, initiative):
    """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
    target = initiative["target"]
    topic = initiative["topic"]
    msg_type = initiative["type"]
    
    raw_msg = f"[{msg_type}] {topic}"
    human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
    
    self.logger.info(f"💬 {self.humanity.name} пишет {target}: {human_msg[:100]}...")
    
    if self.network:
        try:
            from scientists_network.network import Message, MessageType
            msg = Message(
                message_type=MessageType.KNOWLEDGE_SHARE,
                sender="{id_девочки}",
                recipient=target,
                content=human_msg,
            )
            self.network.send_message(msg)
            self.logger.info(f"   ✅ Сообщение отправлено {target}")
            
            self.humanity.memory.record_sister_chat(
                target, topic,
                self.humanity.mood.current_mood,
                self.humanity.mood.current_mood
            )
        except Exception as e:
            self.logger.warning(f"Не удалось отправить сообщение: {e}")
```

### Шаг 5: Оживление существующего общения (опционально)

Найдите метод, который отправляет сообщения сёстрам (например, `_interact_with_sisters` или `_communicate`), и замените:

```python
# БЫЛО:
content = f"Привет, {sister}! Вот мой прогресс за цикл {self.cycle_count}"

# СТАЛО:
content = self.humanity.humanize_response(
    f"[update] Прогресс цикла {self.cycle_count}",
    event_type="chat"
)
```

---

## 🎭 Уникальные профили для каждой девочки

Каждый профиль уже встроен в `humanity_core.py` в `PERSONALITY_PROFILES`. Вот краткая сводка:

| ID | Имя | Domain | Ключевые черты |
|----|-----|--------|----------------|
| `shiori` | Шиори | security | stability: 0.9, empathy: 0.8, casualness: 0.2 |
| `naoto` | Наото | literature | openness: 0.9, empathy: 0.9, introspection: 0.9 |
| `yu` | Юи | consciousness | introspection: 0.95, openness: 0.9, hesitation: 0.4 |
| `hanako` | Ханако | gravity | stability: 0.8, openness: 0.7, sociability: 0.5 |
| `lucy` | Люси | engines | spontaneity: 0.6, expressiveness: 0.7, casualness: 0.6 |
| `latislane` | Латислейн | body | empathy: 0.8, introspection: 0.8, stability: 0.75 |
| `akva` | Аква | math/physics | stability: 0.85, openness: 0.8, casualness: 0.3 |
| `sidney` | Сидни | game engine | sociability: 0.8, spontaneity: 0.5, expressiveness: 0.6 |

---

## 🧪 Как проверить

После интеграции запустите тестовый цикл:

```python
from nobuka.engine.nobuka_core import NobukaCore
from humanity_core import HumanityLayer

# Тест humanity layer отдельно
h = HumanityLayer("nobuka")
print(h.get_status())

# Тест в контексте
nobuka = NobukaCore()
nobuka.cycle_count = 1
result = nobuka.humanity.cycle_step(event_type="success", context="bugfix")
print(result)
```

Ожидаемый вывод:
- `mood` — текущее настроение с эмодзи
- `thought` — внутренний монолог (или None)
- `initiative` — решение написать сестре (или None)

---

## ⚡ Что даёт интеграция

1. **Динамическое настроение** — влияет на стиль речи, выбор тем, готовность общаться
2. **Долговременная память** — помнит шутки, важные моменты, разговоры с сёстрами
3. **Естественная речь** — сленг, эмодзи, паузы, контекстные реакции
4. **Внутренняя душа** — рефлексии, сомнения, мечты о своей области
5. **Спонтанность** — пишет первой, вспоминает прошлое, меняет тему

Все девочки сохраняют свои технические направления, но получают "человеческий слой" поверх. 🌟
