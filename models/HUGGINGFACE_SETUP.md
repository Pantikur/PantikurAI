# 🤗 Настройка Hugging Face для PantikurAI

## Зачем Hugging Face?

Hugging Face — это **GitHub для ML-моделей**:
- ✅ Бесплатное хранилище (неограниченно)
- ✅ Версионирование моделей
- ✅ Быстрая загрузка через CLI
- ✅ Интеграция с PyTorch, TensorFlow, transformers
- ✅ Сообщество и公开的 модели

## 📝 Шаг 1: Создай аккаунт

1. Иди на https://huggingface.co/join
2. Регистрируйся (GitHub, Google или email)
3. Подтверди email

## 🔑 Шаг 2: Получи токен

1. Зайди на https://huggingface.co/settings/tokens
2. Нажми "New token"
3. Выбери тип: **Write** (для загрузки) или **Read** (только скачивание)
4. Скопируй токен (начинается с `hf_...`)

## 💾 Шаг 3: Сохрани токен

```bash
# В терминале:
huggingface-cli login
# Вставь токен когда попросит
```

Или сохрани в `.env`:
```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx
```

## 📤 Шаг 4: Создай репозиторий для моделей

```bash
# Создай репозиторий на сайте:
# https://huggingface.co/new
# Название: pantikur-models
# Приватный или публичный (публичный — бесплатно)

# Или через CLI:
huggingface-cli repo create pantikur-models
```

## 📦 Шаг 5: Загрузи модели

### Способ 1: Через CLI (рекомендуется)
```bash
# Загрузи всю директорию models/
huggingface-cli upload Pantikur/pantikur-models models/ models/
```

### Способ 2: Через Python
```python
from huggingface_hub import HfApi

api = HfApi()
api.upload_folder(
    folder_path="models/",
    repo_id="Pantikur/pantikur-models",
    repo_type="model",
)
```

### Способ 3: Через сайт
1. Зайди в свой репозиторий
2. Нажми "Files" → "Add file" → "Upload files"
3. Перетащи модели

## ⬇️ Шаг 6: Загружай модели в проект

```bash
# Установка
pip install huggingface_hub

# Загрузка конкретной модели
huggingface-cli download Pantikur/pantikur-models chat_model.pth --local-dir models/

# Загрузка всей папки
huggingface-cli download Pantikur/pantikur-models --local-dir models/

# Или через скрипт проекта
python scripts/download_models.py --all
```

## 🔧 Настройка для проекта

### 1. Обнови `scripts/download_models.py`

Замени `repo_id` на свой:
```python
MODELS_CONFIG = {
    "chat_model": {
        "repo_id": "Pantikur/pantikur-models",  # ← твой репозиторий
        "filename": "chat_model.pth",
        ...
    },
}
```

### 2. Загрузи модель

```bash
# Загрузи модель на Hugging Face
huggingface-cli upload Pantikur/pantikur-models models/chat_model.pth chat_model.pth

# Проверь загрузку
huggingface-cli download Pantikur/pantikur-models chat_model.pth --local-dir /tmp/test

# Загрузи в проект
python scripts/download_models.py chat
```

## 📊 Сравнение вариантов хранения

| Платформа | Бесплатно | Лимит | Версии | CLI | ML-интеграция |
|-----------|-----------|-------|--------|-----|---------------|
| **Hugging Face** | ✅ | Неограниченно | ✅ | ✅ | ✅✅✅ |
| GitHub Releases | ✅ | 2 ГБ/релиз | ✅ | ❌ | ❌ |
| Google Drive | ✅ | 15 ГБ | ❌ | ❌ | ❌ |
| Яндекс.Диск | ✅ | 10 ГБ | ❌ | ❌ | ❌ |
| AWS S3 | ❌ | 5 ГБ/мес | ❌ | ✅ | ❌ |

## 🎯 Итог

**Используй Hugging Face** — это стандарт индустрии для ML-моделей:
- Бесплатно
- Быстро
- Профессионально
- Интегрируется с твоим кодом

## ❓ Частые вопросы

**Q: Модели станут меньше?**
A: Нет, размер тот же. Но Hugging Face оптимизирует передачу данных.

**Q: Можно ли квантовать модель?**
A: Да! INT8 квантование уменьшает модель в 4 раза:
```python
import torch
model = torch.load('model.pth')
model_int8 = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
torch.save(model_int8, 'model_int8.pth')  # 52МБ → 13МБ
```

**Q: Что если модель > 2 ГБ?**
A: Hugging Face поддерживает большие файлы. Либо квантуй, либо используй safetensors с shard'ингом.

**Q: Приватный или публичный репозиторий?**
A: Приватный — только ты видишь. Публичный — бесплатно и сообщество может помочь.
