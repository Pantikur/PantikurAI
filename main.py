# main.py — ChatBot API (в честь дня рождения 🎂)

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, validator
from typing import List
import logging
import os
import sys
import textwrap
import subprocess
import threading
import asyncio
import json
import re  # Для парсинга жанра и тегов
from contextlib import asynccontextmanager
from pathlib import Path

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        # Раскомментируй для записи в файл:
        # logging.FileHandler("logs/app.log")
    ]
)
logger = logging.getLogger("main")

# Создаём папку для логов (если нужно)
if not os.path.exists("logs"):
    os.makedirs("logs")

# === Пути ===
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "tokenizer.json"  # ← Новый токенизатор
MODEL_PATH = BASE_DIR / "models" / "model.pth"    # ← Новая модель
CONVERSATIONS_JSON = BASE_DIR / "data" / "conversations.json"

# === Добавляем Wuglarst в путь ===
WUGLARST_DIR = BASE_DIR / "Wuglarst"
if WUGLARST_DIR.exists():
    if str(WUGLARST_DIR) not in sys.path:
        sys.path.insert(0, str(WUGLARST_DIR))
    logger.info(f"✅ Путь добавлен: {WUGLARST_DIR}")
else:
    logger.critical(f"❌ Не найдена директория: {WUGLARST_DIR}")
    raise RuntimeError(f"Не найдена директория: {WUGLARST_DIR}")

# === Загрузка .env (если есть) ===
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
    logger.info("✅ Файл .env загружен")
except ImportError:
    logger.warning("⚠️ python-dotenv не установлен. Пропускаем .env")

# === Глобальная переменная бота и блокировка ===
chatbot = None
CHATBOT_LOCK = threading.RLock()  # Защита при доступе и перезагрузке

# === Импорт ChatBot с резервом ===
def import_chatbot():
    global chatbot
    try:
        from src.chatbot import ChatBot
        logger.info("✅ Импортирован: src.chatbot.ChatBot")
        return ChatBot
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта из src: {e}")

    try:
        import importlib.util
        chatbot_path = WUGLARST_DIR / "src" / "chatbot.py"
        if not chatbot_path.exists():
            raise FileNotFoundError(f"Файл не найден: {chatbot_path}")

        spec = importlib.util.spec_from_file_location("src.chatbot", chatbot_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules["src.chatbot"] = module
        logger.info("✅ Модуль src.chatbot загружен вручную")
        return module.ChatBot
    except Exception as e:
        logger.critical(f"💥 Не удалось загрузить ChatBot: {e}")
        raise


# === Lifespan: загрузка при старте и остановке ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot

    # Проверяем обязательные файлы
    missing = []
    for path, name in [(DATA_PATH, "токенизатор"), (MODEL_PATH, "модель")]:
        if not path.exists():
            logger.critical(f"❌ Файл не найден: {name} → {path}")
            missing.append(name)
    if missing:
        raise RuntimeError(f"Отсутствуют файлы: {', '.join(missing)}")

    # Все файлы на месте
    logger.info("📁 Все необходимые файлы найдены")

    # Проверяем, обновлялся ли conversations.json после последнего обучения
    if CONVERSATIONS_JSON.exists():
        try:
            model_mtime = MODEL_PATH.stat().st_mtime
            data_mtime = CONVERSATIONS_JSON.stat().st_mtime
            if data_mtime > model_mtime:
                logger.warning("🎂 Новые данные в conversations.json — запускаю дообучение...")
                run_retrain_sync()
        except Exception as e:
            logger.error(f"⚠️ Ошибка проверки времени файла: {e}")

    # Загружаем модель
    try:
        logger.info("🔁 Загружаю чат-бот...")
        ChatBot = import_chatbot()
        new_bot = ChatBot(str(MODEL_PATH), str(DATA_PATH))
        with CHATBOT_LOCK:
            chatbot = new_bot
        logger.info("✅ Чат-бот успешно загружен!")
        if hasattr(chatbot, 'dataset') and chatbot.dataset is not None:
            logger.info(f"📚 Обучено на {len(chatbot.dataset)} примерах")
    except Exception as e:
        logger.critical(f"❌ Ошибка инициализации бота: {e}", exc_info=True)
        raise

    yield

    # Очистка при остановке
    logger.info("🛑 Чат-бот остановлен. Хорошего дня! 🎈")


# === FastAPI приложение ===
app = FastAPI(
    title="ChatBot API",
    description="API для Android-приложения PantikurChat",
    version="1.5.0 🎂",
    lifespan=lifespan
)


# === Health Check с деталями ===
@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": app.version,
        "model_loaded": chatbot is not None,
        "files": {
            "model": MODEL_PATH.exists(),
            "data": DATA_PATH.exists(),
            "conversations_json": CONVERSATIONS_JSON.exists()
        }
    }


# === Главная страница ===
@app.get("/")
def home():
    return {
        "message": "🎉 С Днём Рождения! ChatBot API работает!",
        "version": app.version,
        "endpoints": ["/predict", "/retrain", "/ws", "/health"],
        "docs": "/docs"
    }


# === Модели запроса ===
class MessageItem(BaseModel):
    message: str
    is_own: bool

    @validator('message')
    def message_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Сообщение не может быть пустым')
        return v.strip()[:500]


class ChatRequest(BaseModel):
    messages: List[MessageItem]
    mode: str = "chat"

    @validator('mode')
    def mode_must_be_valid(cls, v):
        if v not in ["chat", "world_gen", "narrative"]:
            raise ValueError("mode должен быть 'chat', 'world_gen' или 'narrative'")
        return v


# === Эндпоинт: /predict и / — оба работают ===
@app.post("/predict")
@app.post("/")  # Совместимость с Android
async def predict(request: Request):
    user_agent = request.headers.get("User-Agent", "")
    if "PantikurBot" not in user_agent:
        logger.warning(f"🚫 Заблокирован User-Agent: {user_agent}")
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Невалидный JSON")

    try:
        req = ChatRequest(**body)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Ошибка валидации: {str(e)}")

    if not req.messages:
        raise HTTPException(status_code=422, detail="История сообщений пуста")
    if len(req.messages) > 32:
        raise HTTPException(status_code=422, detail="Слишком длинная история (макс. 32 сообщения)")

    # Безопасное получение chatbot
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Сервис временно недоступен")

    # === Генерация по режимам ===
    try:
        if req.mode == "narrative":
            context = "\n".join([
                f"{'Пользователь' if m.is_own else 'Бот'}: {m.message}"
                for m in req.messages
            ])
            prompt_text = textwrap.dedent(f"""
                Ты — мастер вселенных. Создаёшь глубокие, логичные и атмосферные миры.
                Отвечай только на русском языке.

                Формат:
                Название:
                 - ...
                Описание:
                 - ...
                Законы общества:
                 - ...
                Традиции:
                 - ...
                Внегласные правила:
                 - ...

                История диалога:
                {context}

                Бот:
            """).strip()
            response = local_bot.generate_response([{"message": prompt_text, "is_own": True}], mode="chat").strip()
            if len(response) < 20:
                response = "*Фигура медленно обернулась* 'ты... вернулся... *(внутренне: сердце сжалось)*'"

        elif req.mode == "world_gen":
            last_msg = req.messages[-1].message
            genre = "Фэнтези"
            tags = ""

            # Используем регулярные выражения для парсинга
            genre_match = re.search(r"Жанр:\s*([^.\n]+)", last_msg, re.IGNORECASE)
            if genre_match:
                genre = genre_match.group(1).strip()

            tags_match = re.search(r"Темы:\s*([^.\n]+)", last_msg, re.IGNORECASE)
            if tags_match:
                tags = tags_match.group(1).strip()

            input_msg = f"Создай мир: {genre}"
            if tags:
                input_msg += f", {tags}"

            response = local_bot.generate_response([{"message": input_msg, "is_own": True}], mode="world_gen").strip()

            if not any(kw in response for kw in ["Название:", "Законы общества:", "Традиции:"]):
                response = textwrap.dedent(f"""
                    Название:
                     - {genre}-Мир
                    Законы общества:
                     - Только избранные могут входить в сеть
                    Традиции:
                     - Ежегодный ритуал подключения
                    Внегласные правила:
                     - Слабых отключают без предупреждения
                """).strip()

        else:  # chat
            valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
            response = local_bot.generate_response(valid_msgs, mode="chat").strip()
            if not response:
                response = "Я здесь! 🤖"

        logger.info(f"[API] Обработано | Сообщений: {len(req.messages)} | Mode: {req.mode}")
        return {"response": response}

    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}", exc_info=True)
        return {"response": "Извини, произошла ошибка."}


# === Дообучение (защищённое) ===
RETRAIN_LOCK = threading.Lock()

# НЕ выкидываем ошибку здесь — иначе сломается сборка Docker
RETRAIN_TOKEN = os.getenv("RETRAIN_TOKEN")
if not RETRAIN_TOKEN:
    logger.warning("⚠️ Переменная RETRAIN_TOKEN не задана в .env — /retrain будет отключён")


def run_retrain_sync():
    """Запуск retrain.py в фоне с блокировкой"""
    if not RETRAIN_TOKEN:
        logger.error("❌ RETRAIN_TOKEN не задан — дообучение недоступно")
        return

    if not RETRAIN_LOCK.acquire(blocking=False):
        logger.warning("🔄 Дообучение уже запущено")
        return

    logger.info("🎂 Запускаю дообучение (в честь дня рождения!)...")
    try:
        result = subprocess.run(
            [sys.executable, "retrain.py"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            logger.info("🎉 Дообучение завершено успешно!")
            # Перезагрузка модели
            try:
                ChatBot = import_chatbot()
                new_bot = ChatBot(str(MODEL_PATH), str(DATA_PATH))
                with CHATBOT_LOCK:
                    global chatbot
                    chatbot = new_bot
                logger.info("🔁 Модель перезагружена после обучения")
            except Exception as e:
                logger.error(f"❌ Не удалось перезагрузить модель: {e}")
        else:
            logger.error(f"❌ Ошибка дообучения: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("⏰ Превышен лимит времени (10 мин)")
    except Exception as e:
        logger.error(f"💥 Ошибка запуска: {e}")
    finally:
        RETRAIN_LOCK.release()


@app.post("/retrain")
async def trigger_retrain(request: Request, background_tasks: BackgroundTasks):
    if not RETRAIN_TOKEN:
        raise HTTPException(status_code=503, detail="Дообучение отключено (нет RETRAIN_TOKEN)")

    token = request.headers.get("X-Retrain-Token")
    if token != RETRAIN_TOKEN:
        raise HTTPException(status_code=403, detail="Неверный токен 🎂")

    logger.info("🔧 Запрос на дообучение получен — ставим в фон")
    background_tasks.add_task(run_retrain_sync)
    return {"status": "retrain_started", "detail": "Обучение запущено в фоне!"}


# === WebSocket (временно отключен, не включать) ===
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     logger.info("🟢 Клиент подключился по WebSocket")
#
#     try:
#         async for data in websocket.iter_json():
#             logger.debug(f"📥 Получено: {data}")
#
#             mode = data.get("mode", "chat")
#             messages = data.get("messages", [])
#
#             if not messages:
#                 await websocket.send_json({"error": "Нет сообщений"})
#                 continue
#
#             # Валидация
#             valid_messages = []
#             for msg in messages:
#                 if isinstance(msg, dict) and "message" in msg:
#                     valid_messages.append({
#                         "message": str(msg["message"])[:500],
#                         "is_own": bool(msg.get("is_own", True))
#                     })
#             if not valid_messages:
#                 await websocket.send_json({"error": "Нет валидных сообщений"})
#                 continue
#
#             # Генерация
#             try:
#                 bot_response = chatbot.generate_response(valid_messages, mode=mode)
#             except Exception as e:
#                 logger.error(f"❌ Ошибка генерации: {e}")
#                 bot_response = '{"response": "Извини, произошла ошибка."}'
#
#             # Извлечение текста
#             try:
#                 parsed = json.loads(bot_response)
#                 text = parsed.get("response", "") or parsed.get("world", "") or str(parsed)
#             except Exception:
#                 text = str(bot_response)
#
#             if not text.strip():
#                 text = "Я здесь! 🤖"
#
#             # Потоковая отправка
#             words = text.split()
#             chunk = ""
#             for i, word in enumerate(words):
#                 chunk += word + " "
#                 if len(chunk) > 40 or (i > 0 and i % 10 == 0):
#                     await websocket.send_text(chunk.strip())
#                     chunk = ""
#                     await asyncio.sleep(0.03)  # Имитация печати
#
#             if chunk.strip():
#                 await websocket.send_text(chunk.strip())
#
#             await websocket.send_text("[END]")
#             logger.info("📤 Ответ отправлен полностью")
#
#     except WebSocketDisconnect:
#         logger.info("🔌 Клиент отключился")
#     except Exception as e:
#         logger.error(f"🔴 Ошибка WebSocket: {e}", exc_info=True)
#     finally:
#         logger.info("👋 Клиент отключён")


# === Запуск (для uvicorn) ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info("📌 Сервер готов. Запускаем...")
    uvicorn.run("main:app", host="0.0.0.0", port=port)