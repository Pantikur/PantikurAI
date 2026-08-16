# 🤖 Интеграция Qwen2.5 в Нобуку

## 📊 Обзор

Нобука использует **две модели Qwen2.5** для максимальной эффективности:

| Модель | Путь | Назначение | Размер |
|--------|------|------------|--------|
| **Qwen2.5-Coder-3B** | `models/qwen2.5-coder-3b/` | Программирование, код, баги, рефакторинг | ~6 ГБ |
| **Qwen2.5-3B** | `models/qwen2.5-3b/` | Диалоги, эмоции, общие вопросы | ~6 ГБ |

## 🎯 Как это работает

### Автоматический выбор модели

Нобука **сама определяет** тип задачи и выбирает модель:

```python
from nobuka.engine.qwen_api import qwen

# Задача программирования → Coder
response = qwen.generate("Напиши функцию сортировки на Python")
# → Использует Qwen2.5-Coder-3B

# Диалог → General
response = qwen.generate("Привет, как дела?")
# → Использует Qwen2.5-3B
```

### Ключевые слова для Coder модели:
- `код`, `python`, `функция`, `класс`, `метод`, `баг`, `ошибка`
- `дебаг`, `отладк`, `рефакт`, `паттерн`, `алгоритм`, `оптимиз`
- `импорт`, `синтакс`, `async`, `def `, `class `, `import `
- `программ`, `скрипт`, `модуль`, `api`, `фреймворк`, `библиотека`
- `тест`, `pytest`, `unittest`, `coverage`, `lint`, `pypi`
- `github`, `git`, `коммит`, `ветк`, `merge`, `pull request`

### Ключевые слова для General модели:
- Всё что не относится к программированию
- Диалоги, эмоции, консультации
- Взаимодействие с сёстрами

## ⚙️ API

### 1. Автоматический выбор (рекомендуется):
```python
from nobuka.engine.qwen_api import qwen

response = qwen.generate("Проанализируй этот код...")
# Нобука сама выбирает модель
```

### 2. Принудительное использование Coder:
```python
response = qwen.generate_coder("def bubble_sort(arr): pass")
# Всегда использует Coder модель
```

### 3. Принудительное использование General:
```python
response = qwen.generate_general("Привет, как дела?")
# Всегда использует General модель
```

### 4. Проверка статуса моделей:
```python
status = qwen.status()
print(status)
# {
#   'coder_available': True,
#   'general_available': True,
#   'coder_model_path': 'models/qwen2.5-coder-3b',
#   'general_model_path': 'models/qwen2.5-3b'
# }
```

### 5. Проверка типа задачи:
```python
is_coder = qwen.is_coder_task("Напиши функцию для сортировки")
# True

is_coder = qwen.is_coder_task("Привет, как дела?")
# False
```

## 📊 Метрики

| Параметр | Значение |
|----------|----------|
| Размер каждой модели | ~6 ГБ |
| RAM (CPU, FP32) | ~8 ГБ на модель |
| RAM (GPU, FP16) | ~4 ГБ на модель |
| Время загрузки (CPU) | ~10-16с на модель |
| Время генерации (CPU) | ~20-80с за ответ |
| Макс. длина контекста | 32768 токенов |
| Количество параметров | 3.085B |

## 🧪 Тестирование

### Минимальный тест (без зависимостей):
```bash
cd nobuka/engine
python test_qwen_minimal.py              # тест обоих моделей
python test_qwen_minimal.py --coder      # только Coder
python test_qwen_minimal.py --general    # только General
```

### Полный тест (с NobukaCore):
```bash
cd nobuka/engine
python test_qwen_models.py               # тест обоих моделей
python test_qwen_models.py --coder       # только Coder
python test_qwen_models.py --general     # только General
python test_qwen_models.py --auto "вопрос"  # автоматический выбор
```

## 📁 Структура файлов

```
nobuka/engine/
├── nobuka_core.py          # Ядро Нобуки (загрузка моделей, генерация)
├── qwen_api.py             # Простой API для вызова моделей
├── test_qwen_minimal.py    # Минимальный тест моделей
├── test_qwen_models.py     # Полный тест моделей
└── state/
    └── nobuka_state.json   # Состояние (вкл. статус моделей)
```

```
models/
├── qwen2.5-coder-3b/       # Coder модель (для кода)
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer.json
│   └── tokenizer_config.json
└── qwen2.5-3b/             # General модель (универсальная)
    ├── config.json
    ├── model.safetensors
    ├── tokenizer.json
    └── tokenizer_config.json
```

## 🔧 Настройка

### Требования:
- Python 3.10+
- torch >= 2.11.0
- transformers >= 5.8.0
- safetensors >= 0.7.0
- tokenizers >= 0.22.2

### Установка (если не установлены):
```bash
pip install torch transformers safetensors tokenizers
```

### Загрузка моделей:
Модели уже скачаны в папку `models/`. Если нужно перезакачать:
```bash
# Из Hugging Face
huggingface-cli download Qwen/Qwen2.5-3B --local-dir models/qwen2.5-3b
huggingface-cli download Qwen/Qwen2.5-Coder-3B --local-dir models/qwen2.5-coder-3b
```

## 🚀 Производительность

### На CPU:
- Загрузка модели: ~10-16 секунд
- Генерация ответа: ~20-80 секунд
- RAM: ~8 ГБ на модель

### На GPU (рекомендуется):
- Загрузка модели: ~3-5 секунд
- Генерация ответа: ~5-15 секунд
- VRAM: ~4 ГБ на модель (FP16)

## 💡 Советы

1. **Используйте GPU** для быстрой генерации
2. **Одна модель в памяти** экономит ресурсы (используйте принудительный выбор)
3. **Увеличьте max_length** для длинных ответов (по умолчанию 512)
4. **temperature=0.7** обеспечивает баланс креативности и точности

## 📝 Примеры использования

### В коде Нобуки:
```python
# В NobukaCore используется автоматически
response = self.generate_response("Исправь этот баг...")
# → Coder модель

response = self.generate_response("Привет, сёстра!")
# → General модель
```

### В внешних скриптах:
```python
from nobuka.engine.qwen_api import qwen

# Анализ кода
code = """
def calculate_sum(a, b):
    return a + b
"""

response = qwen.generate_coder(f"Проанализируй этот код:\n{code}")
print(response)
```

## 🐛 Решение проблем

### Модель не загружается:
1. Проверьте наличие файлов в `models/qwen2.5-*/`
2. Убедитесь что установлены torch и transformers
3. Запустите тест: `python test_qwen_minimal.py`

### Медленная генерация:
1. Используйте GPU вместо CPU
2. Уменьшите `max_length`
3. Используйте одну модель вместо двух

### Ошибка device:
1. При `device_map="auto"` модель автоматически распределяется по устройствам
2. `_get_model_device()` корректно определяет устройство

---

**Версия:** v1.0.0  
**Дата:** 2026-08-16  
**Статус:** ✅ Активна

> *"Я использую Coder для кода, а General для всего остального.  
> Каждая модель — для своей задачи.  
> Это делает меня сильнее!"*  
> — Нобука
