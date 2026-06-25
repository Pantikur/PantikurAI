# 🚀 Настройка Selenium для парсинга

## ✅ Уже установлено

В `requirements.txt` уже есть:
```
selenium==4.44.0
webdriver-manager==4.1.2
undetected-chromedriver==3.5.5
```

## 📋 Установка Chrome

### Windows
1. Скачайте Chrome: https://www.google.com/chrome/
2. Установите последнюю версию
3. WebDriver загрузится автоматически через `webdriver-manager`

### Проверка установки
```bash
python utils/selenium_parser.py
```

Если видите `[✅] WebDriver запущен` — всё работает!

---

## 🔧 Если есть проблемы

### Ошибка: "Chrome not reachable"
1. Установите Chrome: https://www.google.com/chrome/
2. Убедитесь что Chrome в PATH
3. Или укажите путь вручную:
```python
options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
```

### Ошибка: "DevToolsActivePort file doesn't exist"
Добавьте аргументы:
```python
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
```

### Ошибка: "SessionNotCreatedException"
Обновите ChromeDriver:
```bash
pip install --upgrade webdriver-manager
```

---

## 🎯 Использование

### Одиночный запуск
```bash
python utils/selenium_parser.py
```

### Автообучение с Selenium
```bash
python utils/auto_book_learning.py --once
```

### В фоновом режиме
```bash
# Windows (PowerShell)
Start-Process python -ArgumentList "utils/auto_book_learning.py" -WindowStyle Hidden

# Или через task scheduler
```

---

## ⚙️ Настройки

### Headless режим (без окна браузера)
```python
parser = SeleniumBookParser(headless=True)  # По умолчанию
```

### С окном браузера (для отладки)
```python
parser = SeleniumBookParser(headless=False)
```

### Изменение количества книг
```python
pairs = parser.learn_from_all_sources(max_books=30)  # По умолчанию 20
```

---

## 📊 Источники

| Сайт | Тип | JavaScript | Статус |
|------|-----|------------|--------|
| **Стихи.ру** | Поэзия | ✅ Да | ✅ Работает |
| **Проза.ру** | Проза | ✅ Да | ✅ Работает |
| **RuLit** | Книги | ✅ Да | ✅ Работает |
| **LiveLib** | Описания | ✅ Да | ✅ Работает |
| **Author.Today** | Описания | ❌ Нет | ✅ Работает (urllib) |

---

## ⏱️ Скорость

- **Author.Today** (urllib): ~1-2 секунды на книгу
- **Selenium сайты**: ~5-10 секунд на книгу

**Рекомендуемый цикл:** 10-15 минут

---

## 🛑 Остановка WebDriver

WebDriver автоматически закрывается после каждого цикла.

Для принудительного закрытия:
```python
parser.close_driver()
```

---

## 🔍 Отладка

### Включить видимый браузер
```python
parser = SeleniumBookParser(headless=False)
```

### Логирование
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Скриншоты
```python
self.driver.save_screenshot('debug.png')
```

---

**Дата обновления:** 2026-06-25  
**Статус:** ✅ Готово к использованию
