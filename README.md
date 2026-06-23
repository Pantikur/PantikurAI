# Pantikur ChatBot

Нейросетевой чат-бот с поддержкой культурных отсылок и диалектов, построенный на PyTorch + FastAPI.  
Интегрирован с Android-приложением через WebSocket и REST API.

---

## 🌟 Особенности

- LSTM-модель на PyTorch для генерации ответов
- Поддержка русских культурных отсылок и региональных фраз
- Режимы: обычный чат, генерация миров, повествование
- WebSocket-потоковый ответ (эффект "печати")
- Автообучение при добавлении новых данных
- Деплой на Timeweb / Render / Docker
- Полная интеграция с Android (`PantikurChat`)

---

## 📁 Структура проекта (актуальная)


```
Pantikur/
│
├── main.py                     ← Основной API (FastAPI + WebSocket)
├── train.py                    ← Обучение основной модели (ретраин)
├── train_narrative.py          ← Обучение повествовательной модели
├── retrain.py                  ← Полный ретраин модели при новых диалогах
├── create_data.py              ← Подготовка данных из JSON
├── inspect_data.py             ← Анализ датасета
├── generate_worlds.py          ← Генерация вымышленных миров
├── add_world_examples.py       ← Добавление примеров миров
├── auto_train.py               ← Автозапуск обучения при изменениях
├── auto_retrain.py             ← Автоматический ретраин
├── inference.py                ← Интерактивный режим (чат в консоли)
│
├── Wuglarst/                   ← Ядро бота (модуль)
│   ├── init.py
│   └── src/
│       ├── chatbot.py             ← Основной класс ChatBot
│       ├── chat_model.py          ← PyTorch модель (LSTM)
│       ├── preprocess.py          ← Токенизация, нормализация
│       ├── cultural_references.py ← Культурные фразы (анекдоты, поговорки)
│       ├── dialect_phrases.py     ← Региональные выражения
│       └── web_search.py          ← Поиск значений слов (опционально)
│
├── data/                       ← Исходные и обработанные данные
│   ├── conversations.jsonl     ← Диалоги пользователей (новые)
│   ├── training_pairs.jsonl    ← Пара "вопрос-ответ" для обучения
│   ├── user_conversations.jsonl ← История сессий
│   ├── knowledge_cache.json    ← Кэш выученных слов
│   └── narrative_examples/
│       └── examples.json       ← Примеры повествований
│
├── models/                     ← Сохранённые веса
│   └── chat_model.pth          ← Обученная PyTorch модель
│
├── scripts/                    ← Вспомогательные скрипты
│   ├── debug_env.py
│   ├── create_data_debug.py
│   └── ...
│
├── configs/                    ← Конфиги модели и обучения
│
├── static/                     ← Статика (если есть)
│
├── knowledge_manager.py        ← Система запоминания новых слов
├── init_knowledge_system.py    ← Инициализация знаний
│
├── Procfile                    ← Запуск через Uvicorn (Timeweb/Render)
├── render.yaml                 ← Деплой на Render.com
├── Dockerfile                  ← Сборка образа
├── docker-compose.yml          ← Локальный запуск в контейнере
│
├── requirements.txt            ← Основные зависимости
├── requirements_knowledge.txt  ← Зависимости для KnowledgeManager
│
├── .env                        ← Переменные окружения
├── .gitignore
│
└── venv/                       ← Виртуальное окружение (не в git)


---

## ⚙️ Режимы работы бота

| Режим         | Описание |
|--------------|--------|
| `chat`       | Обычный разговор с учётом истории. Может искать значения незнакомых слов. |
| `narrative`  | Повествовательный стиль с внутренним монологом (`*(внутренне:...)*`). |
| `world_gen`  | Генерация мира: название, законы, традиции, внегласные правила. |

### Пример запроса:
```json
{
  "messages": [
    {
      "message": "Создай мир: Киберпанк, забвение, нейросети.",
      "is_own": true
    }
  ],
  "mode": "world_gen"
}

🧰 Требования
Python 3.10+
PyTorch
FastAPI
uvicorn[standard]
NumPy, joblib
python-dotenv (опционально)

🔧 Установка
Bash
# 1. Установи зависимости
pip install -r requirements.txt

# 2. Создай .env (если нужно)
cp .env.example .env

# 3. Убедись, что есть:
#    - data/chat_data.pkl (или пересобери через create_data.py)
#    - models/chat_model.pth
▶️ Запуск
Локально (для разработки):
Bash
python main.py
Через Uvicorn (рекомендуется):
Bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
Через Docker:
Bash
docker-compose up --build
🌐 API Эндпоинты
Метод	Путь	Описание
GET	/health	Проверка работоспособности
GET	/	Главная страница
POST	/predict	Ответ на сообщение (JSON)
POST	/	Совместимость с Android
POST	/retrain	Запуск ретраина (фоново)
WS	/ws	WebSocket: потоковый ответ
🚀 Деплой
На Timeweb / Render:

Добавь файл Procfile:


web: uvicorn main:app --host 0.0.0.0 --port $PORT


Убедись, что в main.py есть:


Python
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


Задеплой через GitHub → хостинг автоматически соберёт и запустит.


📦 Обучение модели
Подготовь диалоги в data/conversations.jsonl.
Запусти:
Bash
python create_data.py
python train.py

Новые данные? Запусти:
Bash
python retrain.py


Бот сам запустит ретраин при старте, если найдёт новые .jsonl.


🛠 Поддержка знаний
knowledge_manager.py — система запоминания новых слов.
При встрече неизвестного слова — бот ищет определение.
Сохраняет в data/knowledge_cache.json.
Можно расширить обучение: python update_knowledge.py.
📄 Лицензия
MIT License


---

## ✅ Что изменилось:

| Что было | Что стало |
|--------|----------|
| Устаревшая структура | Актуальная, как в `ls` |
| Нет `Procfile`, `render.yaml` | Теперь они в README |
| Нет про WebSocket | Добавлено описание `/ws` |
| Нет про автообучение | Добавлено `auto_retrain.py`, `retrain.py` |
| Нет `knowledge_manager` | Описано, как работает кэш знаний |

---

Теперь твой `README.md` — **полный, актуальный и профессиональный**.  
Можно коммитить:

```bash
git add README.md
git commit -m "📝 Обновил README: актуальная структура, WebSocket, деплой"
git push origin main