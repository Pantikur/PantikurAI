# Интеграция LLM в Шиори

## Обзор

В систему Шиори интегрированы две модели Qwen2.5:

1. **Qwen2.5-3B** (General) — для общих задач:
   - Генерация естественных ответов в Humanity Layer
   - Анализ угроз
   - Общение с сёстрами
   - Внутренние монологи

2. **Qwen2.5-Coder-3B** (Coder) — для работы с кодом:
   - Генерация патчей для устранения уязвимостей
   - Анализ кода на уязвимости
   - Классификация угроз на основе кода

## Архитектура

```
shiori/
├── engine/
│   ├── config.py              ← Добавлены параметры LLM
│   ├── llm_service.py         ← Новый сервис для работы с моделями
│   ├── shiori_core.py         ← Инициализация LLM
│   ├── patch_manager.py       ← Использование Coder для патчей
│   └── threat_hunter.py       ← Использование Coder для анализа
└── ...
```

## Конфигурация

Параметры в `shiori/engine/config.py`:

```python
# === LLM Модели ===
general_model_path: str = "models/qwen2.5-3b"           # Путь к General модели
coder_model_path: str = "models/qwen2.5-coder-3b"        # Путь к Coder модели
model_device: str = "auto"                        # cpu, cuda, auto
model_max_tokens: int = 1024                      # Максимальная длина ответа
model_temperature: float = 0.7                    # Температура генерации
model_use_flash_attention: bool = False           # Использовать Flash Attention
llm_enabled: bool = True                          # Включить LLM
```

## Использование

### 1. Загрузка моделей

Модели уже загружены в папку `models/`:
- `models/qwen2.5-3b/` — General модель (~6 ГБ)
- `models/qwen2.5-coder-3b/` — Coder модель (~6 ГБ)

### 2. Запуск с LLM

```python
from shiori.engine.config import ShioriConfig
from shiori.engine.shiori_core import ShioriCore

# Создаём конфигурацию
config = ShioriConfig.default()
config.llm_enabled = True  # Включаем LLM

# Запускаем Шиори с LLM
core = ShioriCore(config)
core.run()
```

### 3. Использование LLM напрямую

```python
from shiori.engine.llm_service import ShioriLLMService

# Создаём сервис
llm = ShioriLLMService(config)

# Генерация общего ответа
response = llm.generate_general(
    prompt="Привет! Кто ты?",
    system_prompt="Ты — помощник Шиори. Отвечай кратко и по делу."
)

# Генерация кода
code = llm.generate_coder(
    prompt="Напиши функцию на Python, которая считает факториал числа.",
    code_context="Нужна рекурсивная реализация."
)
```

## Интеграция с компонентами

### Patch Manager
- Использует Coder модель для генерации патчей
- Автоматически переключается на LLM если модель загружена
- Fallback: случайная симуляция

### Threat Hunter
- Использует Coder модель для анализа кода
- Классификация угроз на основе контекста
- Fallback: эвристический анализ

### Humanity Layer
- Использует General модель для генерации естественных ответов
- Более живое и естественное общение
- Fallback: SpeechEngine (шаблоны)

## Требования

- Python 3.10+
- torch >= 2.0
- transformers >= 4.35
- bitsandbytes (опционально, для 4-bit квантизации)

Установка:
```bash
pip install transformers torch bitsandbytes
```

## Производительность

### С GPU (CUDA)
- Используется 4-bit квантизация (BitsAndBytes)
- VRAM: ~4 ГБ на модель
- Скорость: ~50-100 токенов/сек

### Без GPU (CPU)
- Float32/Float16 без квантизации
- RAM: ~12 ГБ на модель
- Скорость: ~5-10 токенов/сек

## Отладка

### Проверка статуса LLM

```python
status = llm.get_status()
print(f"General: {'OK' if status['general_loaded'] else 'FAIL'}")
print(f"Coder: {'OK' if status['coder_loaded'] else 'FAIL'}")
```

### Логи

Все действия LLM логируются:
- Загрузка моделей
- Генерация ответов
- Ошибки

Уровень логирования: `shiori/engine/state/shiori.log`

## Известные проблемы

1. **Нехватка памяти**: Если models не загружаются из-за OOM, попробуйте:
   - Запустить с `llm_enabled=False`
   - Использовать CPU режим
   - Закрыть другие приложения

2. **Медленная генерация**: На CPU генерация может занимать несколько секунд на ответ

3. **Ошибки квантизации**: Если bitsandbytes не установлен, модель загрузится без квантизации (нужно больше VRAM)

## Будущие улучшения

- [ ] Поддержка vLLM для ускорения генерации
- [ ] Кэширование ответов для часто задаваемых вопросов
- [ ] Поддержка более крупных моделей (7B, 14B)
- [ ] Fine-tuning моделей под задачи Шиори
- [ ] Асинхронная генерация для неблокирующих вызовов
