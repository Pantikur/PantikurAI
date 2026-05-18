# main.py — ChatBot API с памятью и поддержкой режимов (улучшенная)

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, validator
from typing import List, Optional
import logging
import os
import sys
import textwrap
import subprocess
import threading
from contextlib import asynccontextmanager
from fastapi import WebSocket
import asyncio
import json

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

# === Добавляем Wuglarst в путь ===
WUGLARST_DIR = os.path.join(BASE_DIR, "Wuglarst")
if os.path.exists(WUGLARST_DIR):
    if WUGLARST_DIR not in sys.path:
        sys.path.insert(0, WUGLARST_DIR)
    logger.info(f"✅ Путь {WUGLARST_DIR} добавлен в sys.path")
else:
    logger.error(f"❌ Директория Wuglarst не найдена: {WUGLARST_DIR}")
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
print("\n" + "=" * 50)
print("🔍 ОТЛАДКА ПУТЕЙ")
print("=" * 50)
print(f"📁 Текущая рабочая директория: {os.getcwd()}")
print(f"📄 Расположение main.py: {__file__}")
print(f"📂 Корень проекта: {BASE_DIR}")
print(f"📦 Wuglarst: {WUGLARST_DIR} → {'✅' if os.path.exists(WUGLARST_DIR) else '❌'}")
if os.path.exists(WUGLARST_DIR):
    src_path = os.path.join(WUGLARST_DIR, "src")
    print(f"📁 src: {src_path} → {'✅' if os.path.exists(src_path) else '❌'}")
    print(f"📄 chatbot.py → {'✅' if os.path.exists(os.path.join(src_path, 'chatbot.py')) else '❌'}")
print("=" * 50 + "\n")

# === Импорт ChatBot (с резервом) ===
try:
    from src.chatbot import ChatBot
    logger.info("✅ Модуль src.chatbot импортирован")
except Exception as e:
    logger.error(f"❌ Ошибка импорта ChatBot: {e}")
    try:
        import importlib.util
        chatbot_path = os.path.join(WUGLARST_DIR, "src", "chatbot.py")
        spec = importlib.util.spec_from_file_location("src.chatbot", chatbot_path)
        chatbot_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chatbot_module)
        sys.modules["src.chatbot"] = chatbot_module
        from src.chatbot import ChatBot
        logger.info("✅ Модуль src.chatbot импортирован вручную")
    except Exception as e2:
        logger.critical(f"💥 Не удалось импортировать ChatBot: {e2}")
        raise

# === Глобальный экземпляр бота ===
chatbot: Optional[ChatBot] = None


# === Lifespan: загрузка при старте ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot

    # Проверяем файлы
    for path, name in [(DATA_PATH, "данные"), (MODEL_PATH, "модель")]:
        if not os.path.exists(path):
            logger.critical(f"❌ Файл {name} не найден: {path}")
            raise RuntimeError(f"Файл не найден: {path}")

    # Автозапуск дообучения
    new_data_files = [
        os.path.join(BASE_DIR, "data", "conversations.jsonl"),
        os.path.join(BASE_DIR, "data", "training_pairs.jsonl"),
        os.path.join(BASE_DIR, "data", "user_conversations.jsonl")
    ]
    if any(os.path.exists(f) for f in new_data_files):
        logger.warning("⚠️ Новые данные — запускаю дообучение...")
        run_retrain()

    # Загрузка модели
    try:
        logger.info("🔁 Загружаю чат-бот...")
        chatbot = ChatBot(MODEL_PATH, DATA_PATH)
        logger.info("✅ Чат-бот успешно загружен")
        if hasattr(chatbot, 'dataset') and chatbot.dataset is not None:
            logger.info(f"📚 Обучено на {len(chatbot.dataset)} примерах")
    except Exception as e:
        logger.critical(f"❌ Ошибка инициализации бота: {e}", exc_info=True)
        raise

    yield
    logger.info("🛑 Чат-бот остановлен")


# === Инициализация FastAPI ===
app = FastAPI(
    title="ChatBot API",
    description="API для Android-приложения PantikurChat",
    version="1.3.0",
    lifespan=lifespan
)


# === Health Check ===
@app.get("/health")
def health():
    return {"status": "ok"}


# === Главная страница ===
@app.get("/")
def home():
    return {
        "message": "ChatBot API работает",
        "version": app.version,
        "endpoints": ["/predict", "/retrain"],
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
        return v.strip()


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
@app.post("/")  # Для совместимости с Android
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
        raise HTTPException(status_code=422, detail=str(e))

    if not req.messages:
        raise HTTPException(status_code=422, detail="История сообщений пуста")

    if chatbot is None:
        logger.error("❌ ChatBot не инициализирован")
        raise HTTPException(status_code=500, detail="Сервис недоступен")

    # === Режим narrative ===
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

        raw_response = chatbot.generate_response(
            [{"message": prompt_text, "is_own": True}],
            mode="chat"
        )
        response = raw_response.strip()
        if len(response) < 20:
            response = (
                "*Фигура медленно обернулась* 'ты... вернулся... "
                "*(внутренне: сердце сжалось)*'"
            )

    # === Режим world_gen ===
    elif req.mode == "world_gen":
        last_msg = req.messages[-1].message
        genre = "Фэнтези"
        tags = "нет дополнительных тегов"

        if "Жанр:" in last_msg:
            try:
                genre = last_msg.split("Жанр:")[1].split(".")[0].strip()
            except: pass
        if "Темы:" in last_msg:
            try:
                tags = last_msg.split("Темы:")[1].split(".")[0].strip()
            except: pass

        input_msg = f"Создай мир: {genre}"
        if tags != "нет дополнительных тегов":
            input_msg += f", {tags}"

        raw_response = chatbot.generate_response(
            [{"message": input_msg, "is_own": True}],
            mode="world_gen"
        )
        response = raw_response.strip()

        fallback_keywords = ["Название:", "Законы общества:", "Традиции:"]
        if not response or len(response) < 50 or not any(kw in response for kw in fallback_keywords):
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

    # === Режим chat ===
    else:
        valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
        response = chatbot.generate_response(valid_msgs, mode="chat").strip()
        if not response:
            response = "Я здесь! 🤖"

    logger.info(f"[API] Обработано | Сообщений: {len(req.messages)} | Mode: {req.mode}")
    return {"response": response}


# === Дообучение ===
def run_retrain():
    logger.info("🔄 Запуск retrain.py...")
    try:
        result = subprocess.run(
            [sys.executable, "retrain.py"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            logger.info("✅ Дообучение завершено")
        else:
            logger.error(f"❌ Ошибка: {result.stderr}")
    except Exception as e:
        logger.error(f"💥 Ошибка запуска: {e}")


@app.post("/retrain", include_in_schema=False)
async def trigger_retrain():
    thread = threading.Thread(target=run_retrain, daemon=True)
    thread.start()
    return {"status": "retrain_started"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🟢 Клиент подключился по WebSocket")

    try:
        async for data in websocket.iter_json():
            logger.debug(f"📥 Получено: {data}")

            mode = data.get("mode", "chat")
            messages = data.get("messages", [])

            if not messages:
                await websocket.send_json({"error": "Нет сообщений"})
                continue

            # Гарантируем формат messages
            valid_messages = []
            for msg in messages:
                if isinstance(msg, dict) and "message" in msg:
                    valid_messages.append({
                        "message": str(msg["message"])[:500],  # Ограничение длины
                        "is_own": bool(msg.get("is_own", True))
                    })

            if not valid_messages:
                await websocket.send_json({"error": "Нет валидных сообщений"})
                continue

            # Генерируем ответ
            try:
                bot_response = chatbot.generate_response(valid_messages, mode=mode)
            except Exception as e:
                logger.error(f"❌ Ошибка генерации: {e}")
                bot_response = '{"response": "Извини, произошла ошибка."}'

            # Извлекаем текст
            try:
                parsed = json.loads(bot_response)
                text = parsed.get("response", "") or parsed.get("world", "")
                if not text:
                    text = str(parsed)
            except Exception:
                text = str(bot_response)

            if not text.strip():
                text = "Я здесь! 🤖"

            # Потоковая отправка "по словам"
            words = text.split()
            chunk = ""
            for i, word in enumerate(words):
                chunk += word + " "
                if len(chunk) > 40 or (i > 0 and i % 10 == 0):  # Каждые ~10 слов
                    await websocket.send_text(chunk.strip())
                    chunk = ""
                    await asyncio.sleep(0.05)  # Имитация печати

            if chunk.strip():
                await websocket.send_text(chunk.strip())

            await websocket.send_text("[END]")  # Сигнал окончания
            logger.info("📤 Ответ отправлен полностью")

    except Exception as e:
        logger.error(f"🔴 WebSocket ошибка: {e}", exc_info=True)
        try:
            await websocket.close()
        except:
            pass
    finally:
        logger.info("🔌 Клиент отключился от WebSocket")

logger.info("📌 Сервер готов. Запустите: uvicorn main:app --host 0.0.0.0 --port 8000")
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))  # Timeweb передаёт PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port)