# ⚙️ Системная инициализация Айко

## Запуск

```bash
# Инициализация ядра
python -m ayiko.engine.run

# Демо-режим
python -m ayiko.engine.run --demo
```

## Инициализация состояния

При первом запуске Айко:
1. Создаёт структуру директорий
2. Инициализирует базу знаний
3. Загружает конфигурацию
4. Подключается к сети учёных

## Мониторинг

```bash
# Проверить состояние
cat ayiko/engine/state/ayiko_state.json

# Посмотреть логи
cat ayiko/engine/state/ayiko.log

# Проверить базу знаний
cat ayiko/engine/state/knowledge_base.json
```

## Остановка

```
Ctrl+C — graceful shutdown
```

---

**Айко готова к работе!** 📚
