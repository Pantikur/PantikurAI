# main.py — ChatBot API с памятью и поддержкой режимов

from click import prompt
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import logging
import os
import sys
import textwrap
import subprocess
import threading
import sys
from fastapi import BackgroundTasks
from contextlib import asynccontextmanager


# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# === Определяем корень проекта ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "chat_data.pkl")
MODEL_PATH = os.path.join(BASE_DIR, "models", "chat_model.pth")

# === Добавляем Wuglarst в путь для импорта src.chatbot ===
WUGLARST_DIR = os.path.join(BASE_DIR, "Wuglarst")
if os.path.exists(WUGLARST_DIR):
    if WUGLARST_DIR not in sys.path:
        sys.path.insert(0, WUGLARST_DIR)
    logger.info(f"✅ Путь {WUGLARST_DIR} добавлен в sys.path")
else:
    logger.warning(f"⚠️ Директория Wuglarst не найдена: {WUGLARST_DIR}")
    raise FileNotFoundError(f"Не найдена директория: {WUGLARST_DIR}")

# === Загружаем .env (если есть) ===
dotenv_path = os.path.join(BASE_DIR, ".env")
if os.path.exists(dotenv_path):
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path, override=False)
        logger.info("✅ Файл .env загружен")
    except ImportError:
        logger.warning("⚠️ python-dotenv не установлен. Пропускаем .env")


# === Отладка путей ===
print("\n" + "="*50)
print("🔍 ОТЛАДКА ПУТЕЙ")
print("="*50)
print(f"📁 Текущая рабочая директория: {os.getcwd()}")
print(f"📄 Расположение main.py: {__file__}")
print(f"📂 Корень проекта (BASE_DIR): {BASE_DIR}")
print(f"📦 Путь к Wuglarst: {WUGLARST_DIR}")
print(f"✅ Существует ли папка Wuglarst? {os.path.exists(WUGLARST_DIR)}")

if os.path.exists(WUGLARST_DIR):
    src_path = os.path.join(WUGLARST_DIR, "src")
    init_py = os.path.join(src_path, "__init__.py")
    chatbot_py = os.path.join(src_path, "chatbot.py")
    print(f"✅ Существует ли Wuglarst/src/? {os.path.exists(src_path)}")
    print(f"✅ Существует ли Wuglarst/src/__init__.py? {os.path.exists(init_py)}")
    print(f"✅ Существует ли Wuglarst/src/chatbot.py? {os.path.exists(chatbot_py)}")

print(f"📋 sys.path:")
for i, p in enumerate(sys.path):
    print(f"  {i}: {p}")
print("="*50 + "\n")


# === Импорт чат-бота (вручную, если стандартный не работает) ===
try:
    from src.chatbot import ChatBot
    logger.info("✅ Модуль src.chatbot импортирован")
except Exception as e:
    logger.error(f"❌ Ошибка импорта ChatBot: {e}")
    # Попробуем вручную
    try:
        import importlib.util
        chatbot_path = os.path.join(WUGLARST_DIR, "src", "chatbot.py")
        spec = importlib.util.spec_from_file_location("src.chatbot", chatbot_path)
        chatbot_module = importlib.util.module_from_spec(spec)
        sys.modules["src.chatbot"] = chatbot_module
        spec.loader.exec_module(chatbot_module)
        from src.chatbot import ChatBot
        logger.info("✅ Модуль src.chatbot импортирован вручную")
    except Exception as e2:
        logger.error(f"❌ Не удалось импортировать даже вручную: {e2}")
        raise


# === Глобальный экземпляр бота ===
chatbot = None


# === Lifespan: загрузка модели при старте ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot

    # Проверяем наличие файлов
    for path, name in [(DATA_PATH, "данные"), (MODEL_PATH, "модель")]:
        if not os.path.exists(path):
            logger.error(f"❌ Файл {name} не найден: {path}")
            raise RuntimeError(f"Файл не найден: {path}")

    # 🔍 Автозапуск retrain при наличии новых данных
    new_data_files = [
        os.path.join(BASE_DIR, "data", "conversations.jsonl"),
        os.path.join(BASE_DIR, "data", "training_pairs.jsonl"),
        os.path.join(BASE_DIR, "data", "user_conversations.jsonl")
    ]

    if any(os.path.exists(f) for f in new_data_files):
        logger.warning("⚠️ Обнаружены новые данные — запускаю дообучение...")
        run_retrain()  # Теперь работает! 🎉

    # Загружаем модель
    try:
        logger.info("🔁 Загружаю чат-бот...")
        chatbot = ChatBot(MODEL_PATH, DATA_PATH)
        
        logger.info("✅ Чат-бот успешно загружен и готов к работе")
        if hasattr(chatbot, 'dataset') and chatbot.dataset is not None:
            logger.info(f"📚 Модель обучена на {len(chatbot.dataset)} примерах")
        else:
            logger.warning("⚠️ Данные обучения (dataset) недоступны для подсчёта")
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации чат-бота: {e}")
        raise

    yield
    logger.info("🛑 Чат-бот остановлен")


# === Инициализация FastAPI ===
app = FastAPI(
    title="ChatBot API",
    description="API для Android-приложения PantikurChat с поддержкой контекста и режимов",
    version="1.2.0",
    lifespan=lifespan
)
logger.info("✅ FastAPI приложение создано")


# === Health Check ===
@app.get("/health")
def health():
    return {"status": "ok"}


# === Главная страница ===
@app.get("/")
def home():
    return {
        "message": "ChatBot API работает",
        "version": "1.2.0",
        "endpoints": ["/predict"],
        "docs": "/docs"
    }


# === Модели запроса ===
class MessageItem(BaseModel):
    message: str
    is_own: bool  # True = пользователь, False = бот


class ChatRequest(BaseModel):
    messages: List[MessageItem]
    mode: str = "chat"  # Режим: "chat" или "world_gen"


# === Основной эндпоинт: обработка диалога с памятью и режимом ===
@app.post("/predict")
async def predict_raw(request: Request):
    # 🔐 Проверка User-Agent
    user_agent = request.headers.get("User-Agent", "")
    if "PantikurBot" not in user_agent:
        logger.warning(f"🚫 Заблокирован запрос с User-Agent: {user_agent}")
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    try:
        # Парсим JSON
        json_body = await request.json()
        messages_json = json_body.get("messages")
        mode = json_body.get("mode", "chat")

        if not messages_json or not isinstance(messages_json, list):
            raise HTTPException(status_code=422, detail="Ожидается массив 'messages'")

        if len(messages_json) == 0:
            raise HTTPException(status_code=422, detail="История сообщений пуста")

        # Валидируем каждое сообщение
        valid_messages = []
        for item in messages_json:
            msg = item.get("message", "").strip()
            is_own = item.get("is_own", False)
            if msg:
                valid_messages.append({"message": msg, "is_own": is_own})

        if not valid_messages:
            raise HTTPException(status_code=422, detail="Все сообщения пустые")

        # Проверка модели
        if chatbot is None:
            logger.error("❌ ChatBot не инициализирован")
            raise HTTPException(status_code=500, detail="Сервис временно недоступен")

        # === ОБРАБОТКА РЕЖИМА narrative ===
        if mode == "narrative":
            last_message = valid_messages[-1]["message"]

            # 🌐 Формируем системный промпт для повествовательного стиля с внутренним состоянием
            full_context = "\n".join([f"{'Пользователь' if m['is_own'] else 'Бот'}: {m['message']}" for m in valid_messages])
            prompt = (
    "Ты — мастер вселенных. Ты создаёшь глубокие, логичные и атмосферные миры.\\n"
    "Отвечай только на русском языке.\\n"
    "Формат ответа:\\n"
    "Название:\\n - ...\\n"
    "Описание:\\n - ...\\n"
    "Законы общества:\\n - ...\\n"
    "Традиции:\\n - ...\\n"
    "Внегласные правила:\\n - ...\\n"
    "\\n"
    "Пример:\\n"
    "Название:\\n - Падший Киберпанк\\n"
    "Описание:\\n - Город, где память можно купить на чёрном рынке.\\n"
    "Законы общества:\\n - Все нейроимпланты должны быть зарегистрированы.\\n"
    "Традиции:\\n - Ежегодный фестиваль забвения.\\n"
    "Внегласные правила:\\n - Не спрашивай, чья это память.\\n"
    "\\n"
    "История диалога:\\n"
    f"{full_context}\\n"
    "Бот:"
)

            response = chatbot.generate_response(
                [{"message": prompt, "is_own": True}],
                mode="chat"  # передаём как обычный чат, но с промптом
            )
            response = response.strip()

            # Fallback — на случай пустого ответа
            if not response or len(response) < 10:
                response = (
                    "*Фигура медленно обернулась в полумраке* 'ты... вернулся... "
                    "*(внутренне: сердце сжалось. Я не должна была этого ждать)*'"
                )

        elif mode == "world_gen":
            last_message = valid_messages[-1]["message"]

            # Извлекаем жанр и темы
            try:
                primary_genre = last_message.split("Жанр:")[1].split(".")[0].strip()
            except (IndexError, Exception):
                primary_genre = "Фэнтези"

            try:
                secondary_tags = last_message.split("Темы:")[1].split(".")[0].strip()
            except (IndexError, Exception):
                secondary_tags = "нет дополнительных тегов"

            # 🚀 Формируем запрос как в обучающих данных!
            user_input = f"Создай мир: {primary_genre}, {secondary_tags}"
            if ", нет дополнительных тегов" in user_input:
                user_input = user_input.replace(", нет дополнительных тегов", "")

            # Передаём боту как обычное сообщение
            response = chatbot.generate_response(
                [{"message": user_input, "is_own": True}],
                mode="world_gen"
            )
            response = response.strip()

            # Fallback — только если совсем пусто
            if not response or len(response) < 10 or not any(kw in response for kw in ["Название:", "Законы общества:", "Традиции:", "Внегласные правила:"]):
                response = textwrap.dedent(f"""
                    Название:
                     - Мир {primary_genre}
                    Законы общества:
                     - Только избранные могут входить в сеть
                    Традиции:
                     - Ежегодный ритуал подключения к источнику
                    Внегласные правила:
                     - Слабых отключают без предупреждения
                """).strip()

        else:
            # Обычный чат
            response = chatbot.generate_response(valid_messages, mode=mode)
            response = response.strip() or "Я здесь! 🤖"

        logger.info(f"[API] Диалог обработан. Сообщений: {len(valid_messages)}, Mode: {mode}")

        return {"response": response}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка сервера")

# === Функция для дообучения (доступна везде) ===
def run_retrain():
    """Запускает retrain.py и логирует результат"""
    logger.info("🔄 Начинаю процесс дообучения через retrain.py...")
    try:
        result = subprocess.run(
            [sys.executable, "retrain.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=600  # 10 минут
        )
        if result.returncode == 0:
            logger.info("✅ Дообучение успешно завершено")
            logger.debug(f"stdout: {result.stdout}")
        else:
            logger.error(f"❌ Ошибка при дообучении")
            logger.error(f"stderr: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("⏰ Таймаут: дообучение заняло слишком много времени")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка при запуске retrain.py: {e}")


# === Эндпоинт: ручной запуск дообучения ===
@app.post("/retrain")
async def trigger_retrain():
    """
    Запускает дообучение в фоне.
    """
    thread = threading.Thread(target=run_retrain, daemon=True)
    thread.start()

    return {
        "status": "retrain_started",
        "message": "Процесс дообучения запущен в фоне",
        "note": "Проверьте логи сервера для деталей"
    }

logger.info("📌 Сервер настроен. Ожидание подключений...")