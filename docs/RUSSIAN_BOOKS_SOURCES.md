# 📚 Русскоязычные источники книг

## ✅ Рабочие источники (используются)

### 1. Author.Today
**Статус:** ✅ Полностью работает  
**Тип:** Описания/аннотации (300-1000 символов)  
**URL:** `https://author.today/work/genre/{genre}?accessType=free`  
**Кодировка:** UTF-8  
**Метод:** urllib (без JavaScript)

**Жанры:**
- фэнтези, попаданцы, фантастика, мистика
- детектив, приключения, психология, философия
- современная проза, боевое фэнтези, городское фэнтези
- научная фантастика, альтернативная история, литрпг
- ужасы, романтика, драма, любовное фэнтези

**Плюсы:**
- ✅ Стабильно работает
- ✅ Бесплатный доступ
- ✅ Русскоязычные книги
- ✅ Нет JavaScript
- ✅ Быстро (~1-2 сек на книгу)
- ✅ ~15-30 пар за цикл

**Минусы:**
- ❌ Только описания (не полные тексты)

**Парсер:** `utils/author_today_parser.py`

---

### 2. Стихи.ру (Selenium)
**Статус:** ✅ Работает с Selenium  
**Тип:** Полные тексты (поэзия)  
**URL:** `https://stihi.ru/`  
**Кодировка:** UTF-8  
**Метод:** Selenium WebDriver

**Плюсы:**
- ✅ Полные тексты
- ✅ Много авторов
- ✅ Бесплатно
- ✅ Русский язык

**Минусы:**
- ⏱️ Медленно (~5-10 сек на книгу)
- 🖥️ Требует Chrome + Selenium

**Парсер:** `utils/selenium_parser.py`

---

### 3. Проза.ру (Selenium)
**Статус:** ✅ Работает с Selenium  
**Тип:** Полные тексты (проза)  
**URL:** `https://proza.ru/`  
**Кодировка:** UTF-8  
**Метод:** Selenium WebDriver

**Плюсы:**
- ✅ Полные тексты
- ✅ Много авторов
- ✅ Бесплатно
- ✅ Русский язык

**Минусы:**
- ⏱️ Медленно (~5-10 сек на книгу)
- 🖥️ Требует Chrome + Selenium

**Парсер:** `utils/selenium_parser.py`

---

### 4. RuLit (Selenium)
**Статус:** ✅ Работает с Selenium  
**Тип:** Книги (описания + главы)  
**URL:** `https://rulit.me/`  
**Кодировка:** UTF-8  
**Метод:** Selenium WebDriver

**Жанры:** fantasy, sf, detektiv, priklyucheniya, proza

**Плюсы:**
- ✅ Много книг
- ✅ Бесплатно
- ✅ Русский язык

**Минусы:**
- ⏱️ Медленно (~5-10 сек на книгу)
- 🖥️ Требует Chrome + Selenium

**Парсер:** `utils/selenium_parser.py`

---

### 5. LiveLib (Selenium)
**Статус:** ✅ Работает с Selenium  
**Тип:** Описания + аннотации  
**URL:** `https://www.livelib.ru/`  
**Кодировка:** UTF-8  
**Метод:** Selenium WebDriver

**Плюсы:**
- ✅ Качественные описания
- ✅ Рецензии
- ✅ Русский язык

**Минусы:**
- ⏱️ Медленно (~5-10 сек на книгу)

**Парсер:** `utils/selenium_parser.py`

---

## 📊 Сравнение источников

| Источник | Тип текста | Метод | Скорость | Статус |
|----------|------------|-------|----------|--------|
| **Author.Today** | Описания (300-1000) | urllib | ⚡ Быстро | ✅ Используется |
| **Стихи.ру** | Полные тексты | Selenium | 🐌 Медленно | ✅ Используется |
| **Проза.ру** | Полные тексты | Selenium | 🐌 Медленно | ✅ Используется |
| **RuLit** | Описания + главы | Selenium | 🐌 Медленно | ✅ Используется |
| **LiveLib** | Описания + аннотации | Selenium | 🐌 Медленно | ✅ Используется |

---

## 📈 Статистика

**За цикл (10 минут):**
- Author.Today: 5 книг × 3 пары = **~15 пар** (быстро)
- Selenium: 5 книг × 3 пары = **~15 пар** (медленно)
- **Итого: ~30 пар за цикл**

**За день (144 цикла):**
- **~4320 пар** (теоретически)
- **~1440 книг** (с учётом дубликатов ~500-700 уникальных)

---

## 🚀 Использование

### Автообучение (рекомендуется)
```bash
# Запуск каждые 10 минут
python utils/auto_book_learning.py

# Одиночный цикл
python utils/auto_book_learning.py --once

# С настройками
python utils/auto_book_learning.py --cycle 15 --books 10
```

### Прямой вызов парсеров

#### Author.Today (быстро, описания)
```python
from utils.author_today_parser import AuthorTodayParser

parser = AuthorTodayParser()
pairs = parser.learn_from_author_today(
    genres=["фэнтези", "попаданцы"],
    max_books=5
)
print(f"Собрано {len(pairs)} пар")
```

#### Selenium (полные тексты)
```python
from utils.selenium_parser import SeleniumBookParser

parser = SeleniumBookParser(headless=True)
try:
    pairs = parser.learn_from_all_sources(max_books=10)
    print(f"Собрано {len(pairs)} пар")
finally:
    parser.close_driver()
```

---

## 🔧 Установка Selenium

### 1. Установите зависимости
```bash
pip install -r requirements.txt
```

### 2. Установите Google Chrome
- Windows: https://www.google.com/chrome/
- Linux: `sudo apt install google-chrome-stable`

### 3. Проверка
```bash
python utils/selenium_parser.py
```

Если видите `[✅] WebDriver запущен` — всё работает!

**Подробная инструкция:** `docs/SELENIUM_SETUP.md`
