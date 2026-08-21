# 🚀 Wuglarst Autonomous — Инструкция по запуску

## Что создано

✅ **Wuglarst Autonomous Server** — постоянный онлайн-сервер для 13 девочек
✅ **Daemon** — фоновый процесс с автосбросом
✅ **Интеграция с Сидни** — автоматическое подключение
✅ **Автозапуск Windows** — старт при включении компьютера

---

## 📋 Шаг 1: Установка

```bash
# Перейдите в папку Wuglarst
cd d:\NewCod\Pantikur\Wuglarst

# Запустите установку
python setup_autonomous.py
```

Или вручную:
```bash
pip install fastapi uvicorn pydantic
```

---

## 📋 Шаг 2: Запуск

### Вариант А: Через демон (рекомендуется)

```bash
cd d:\NewCod\Pantikur\Wuglarst
python daemon.py start
```

### Вариант Б: Простой запуск

```bash
cd d:\NewCod\Pantikur\Wuglarst
python server_autonomous.py
```

### Вариант В: Через BAT файл

Дважды кликните по `start_autonomous.bat`

---

## 📋 Шаг 3: Установка автозапуска

```bash
cd d:\NewCod\Pantikur\Wuglarst
python daemon.py install
```

Создаётся файл автозапуска:
```
C:\Users\YOUR_USER\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Wuglarst_start.bat
```

---

## 📋 Шаг 4: Проверка

Откройте браузер:
```
http://localhost:8001
```

Проверьте здоровье:
```
http://localhost:8001/health
```

---

## 📋 Шаг 5: Запуск Сидни

```bash
cd d:\NewCod\Pantikur
python tests/test_sidney.py
```

Сидни автоматически подключится к Wuglarst и покажет свой статус.

---

## 🎮 Управление

```bash
# Статус
python daemon.py status

# Остановка
python daemon.py stop

# Перезапуск
python daemon.py restart
```

---

## 📊 Что вы видите

После запуска вы увидите:

1. **Веб-интерфейс** — карточки всех 13 девочек
2. **Статусы** — working, thinking, idle, error, offline
3. **Время работы** — сервер работает 24/7
4. **Журнал событий** — всё что происходит
5. **Онлайн счётчик** — сколько девочек активны

---

## 🔗 Связь Сидни ↔ Wuglarst

```
┌──────────────┐         ┌──────────────────┐
│   Сидни      │         │   Wuglarst       │
│              │         │                  │
│ - 8 движков  │──────→  │ - Веб интерфейс  │
│ - AI         │         │ - WebSocket      │
│ - Network    │         │ - REST API       │
│ - Scripting  │         │ - Автосохранение │
│              │         │                  │
└──────────────┘         └──────────────────┘
```

Сидни отправляет:
- Статус работы движков
- Уровень знаний
- Циклы саморазвития
- События и оптимизации

Wuglarst показывает:
- Карточку Сидни с аватаром 🎮
- Текущую задачу
- Статус работы
- Визуальную позицию на карте

---

## 💡 Советы

1. **Запускайте Wuglarst первым** — чтобы Сидни могла подключиться
2. **Используйте daemon.py** — для постоянной работы
3. **Установите автозапуск** — чтобы работало после перезагрузки
4. **Смотрите логи** — `logs/wuglarst_daemon.log`

---

## 🆘 Проблемы

### Порт 8001 занят

```bash
# Найдите процесс
netstat -ano | findstr :8001

# Убейте процесс
taskkill /F /PID <PID>
```

### Сидни не подключается

```bash
# Проверьте Wuglarst
curl http://localhost:8001/health

# Если ошибка — запустите Wuglarst
python daemon.py start
```

### Ошибки импорта

```bash
# Установите зависимости
pip install fastapi uvicorn pydantic
```

---

## 📚 Документация

- [Подробная документация](README_AUTONOMOUS.md)
- [Полное руководство](README_FULL.md)
- [Старый сервер](server.py) — для сравнения

---

## ✅ Готово!

Теперь у вас есть:
- ✅ Постоянный сервер для 13 девочек
- ✅ Автозапуск при старте Windows
- ✅ Визуальный интерфейс
- ✅ Интеграция с Сидни
- ✅ Автосохранение и автосброс

Сервер работает 24/7, даже когда компьютер выключен (через автозапуск)!
