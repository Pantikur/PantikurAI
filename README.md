# Pantikur ChatBot

Neural network chatbot with cultural and dialect support, built with PyTorch and FastAPI.

## Features

- LSTM-based neural network for conversational AI
- Support for Russian cultural references and regional dialects
- FastAPI web interface for Android integration
- Docker and Docker Compose support
- Deployable on Render.com
- Text preprocessing and vocabulary management

## Project Structure

```
Pantikur/
│
├── main.py                  ← Основной API (FastAPI)
├── train.py                 ← Обучение модели диалогов
├── train_narrative.py       ← Обучение повествовательной модели
├── create_data.py           ← Подготовка данных из JSON
├── inspect_data.py          ← Анализ датасета
├── generate_worlds.py       ← Генерация вымышленных миров
├── add_world_examples.py    ← Добавление примеров миров в данные
├── auto_train.py            ← Автозапуск обучения при изменениях
│
├── Wuglarst/                ← Ядро чат-бота (модуль)
│   ├── init.py
│   └── src/
│       ├── chatbot.py             ← Основной класс ChatBot
│       ├── chat_model.py          ← PyTorch модель (LSTM)
│       ├── preprocess.py          ← Токенизация, нормализация
│       ├── cultural_references.py ← Культурные фразы (анекдоты, поговорки)
│       ├── dialect_phrases.py     ← Региональные выражения (уральский, север и др.)
│       └── web_search.py          ← Поиск значений слов (опционально)
│
├── data/                    ← Исходные и обработанные данные
│   ├── conversations.json   ← Диалоги пользователей
│   ├── training_data.json   ← Обучающие пары "вопрос-ответ"
│   └── narrative_examples/
│       └── examples.json    ← Примеры повествований и описаний миров
│
├── models/                  ← Сохранённые веса
│   └── chat_model.pth       ← Обученная PyTorch модель
│
├── static/                  ← Статика (веб-интерфейс, если есть)
│   └── index.html
│
├── scripts/                 ← Вспомогательные скрипты
│   ├── train.py
│   ├── create_data_debug.py
│   ├── debug_env.py
│   └── inspect_data.py
│
├── .env                     ← Переменные окружения
├── .env.example             ← Шаблон .env
├── .gitignore
├── requirements.txt         ← Зависимости Python
├── Dockerfile               ← Для сборки образа
├── docker-compose.yml       ← Локальный запуск в контейнере
├── render.yaml              ← Деплой на Render.com
├── run.py                   ← Альтернативный запуск (если используется)
│
├── temp_debug.py            ← Временные скрипты (удалить в продакшене)
├── test_joblib.pkl
├── generated_worlds.json
│
└── venv/                    ← Виртуальное окружение (не в git)
```

---

## ⚙️ Режимы работы бота

| Режим         | Описание |
|--------------|--------|
| `chat`       | Обычный разговор с учётом истории |
| `narrative`  | Повествовательный стиль с внутренним монологом (`*(внутренне:...)*`) |
| `world_gen`  | Генерация мира по шаблону: название, законы, традиции, правила |

Пример запроса:
```json
{
  "messages": [{"message": "Создай мир: Киберпанк, забвение, нейросети.", "is_own": true}],
  "mode": "world_gen"
}

## Requirements

- Python 3.10+
- PyTorch
- FastAPI
- uvicorn
- NumPy
- python-dotenv

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Set up environment variables:
```
copy .env.example .env
```

3. Train the model (if needed):
```
python scripts/train.py
```

## Running the Application

### Local Development
```
python main.py
```

### With Docker
```
docker-compose up --build
```

## API Endpoints

- `GET /health` - Health check
- `GET /` - Home endpoint
- `POST /predict` - Chat prediction (Android integration)

## Deployment

The application is configured for deployment on [Render.com](https://render.com):

1. The `render.yaml` file configures the web service
2. Dockerfile builds the container image
3. Application runs on port specified by ${PORT} environment variable

## Data Structure

The chatbot uses preprocessed data in `Wuglarst/data/chat_data.pkl` containing:
- `input_sequences` and `target_sequences` - training data
- `word_to_idx` and `idx_to_word` - vocabulary mapping
- `vocab_size` and `max_length` - model parameters

Source conversations are stored in `data/conversations.json`.

## Training Custom Model

1. Prepare your conversation data in `data/conversations.json`
2. Run the training script:
```
python scripts/train.py
```
3. The trained model will be saved to `Wuglarst/models/chat_model.pth`

## Configuration Recommendations

1. Remove duplicate data files:
   - `data/chat_data.pkl` (keep only `Wuglarst/data/chat_data.pkl`)
   - `models/chat_model.pth` (keep only `Wuglarst/models/chat_model.pth`)

2. Update `.env.example` with proper API_KEY

3. Ensure Dockerfile uses ${PORT} instead of hardcoded 10000

## License

[MIT License](LICENSE)