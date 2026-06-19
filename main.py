# main.py — ChatBot API

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
import random
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime

# === Настройка логирования ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        # logging.FileHandler("logs/app.log")  # ← раскомментируйте для логов в файл
    ]
)
logger = logging.getLogger("main")

# Создаём папку для логов (если нужно)
if not os.path.exists("logs"):
    os.makedirs("logs")

# === Пути ===
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "chat_model.pth"
DATA_PATH = BASE_DIR / "data" / "tokenizer.json"
CONVERSATIONS_JSON = BASE_DIR / "data" / "conversations.json"

# === Добавляем Wuglarst/src в путь (точно для импорта src.chatbot) ===
WUGLARST_DIR = BASE_DIR / "Wuglarst"
WUGLARST_SRC_DIR = WUGLARST_DIR / "src"

if WUGLARST_SRC_DIR.exists():
    if str(WUGLARST_DIR) not in sys.path:
        sys.path.insert(0, str(WUGLARST_DIR))
        logger.info(f"✅ Путь added: {WUGLARST_DIR} (родитель для Wuglarst/src/)")
elif WUGLARST_DIR.exists():
    if str(WUGLARST_DIR) not in sys.path:
        sys.path.insert(0, str(WUGLARST_DIR))
        logger.warning(f"⚠️ Использую Wuglarst (а не Wuglarst/src) — проверьте структуру: {WUGLARST_DIR}")
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

# === GIGACHAT_TOKEN для потенциального self-teaching ===
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN")
if GIGACHAT_TOKEN:
    logger.info("✅ GIGACHAT_TOKEN найден — можно настроить self-teaching")
else:
    logger.warning("⚠️ GIGACHAT_TOKEN не задан — дообучение без данных от GigaChat")
# === КОНЕЦ GIGACHAT_TOKEN ===

# === Глобальная переменная бота и блокировка ===
chatbot = None
CHATBOT_LOCK = threading.RLock()  # Защита при доступе и перезагрузке
    # === Глобальная переменная WebSearch ===
web_search = None
WEBSH_LOCK = threading.Lock()  # Защита при доступе к web_search

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
    

    start_lifespan = asyncio.get_event_loop().time()
    logger.info("🔄 Старт lifespan...")

    # Проверяем обязательные файлы
    missing = []
    for path, name in [(DATA_PATH, "токенизатор"), (MODEL_PATH, "модель")]:
        if not path.exists():
            logger.critical(f"❌ Файл не найден: {name} → {path}")
            missing.append(name)
    if missing:
        raise RuntimeError(f"Отсутствуют файлы: {', '.join(missing)}")
    
    

    logger.info(f"📁 Все необходимые файлы найдены за {asyncio.get_event_loop().time() - start_lifespan:.2f} сек")

    # === Асинхронный запуск дообучения при старте (не блокирует запуск) ===
    async def launch_retrain_async():
        await asyncio.to_thread(run_retrain_sync)

    if CONVERSATIONS_JSON.exists():
        try:
            model_mtime = MODEL_PATH.stat().st_mtime
            data_mtime = CONVERSATIONS_JSON.stat().st_mtime
            if data_mtime > model_mtime:
                logger.warning("🎂 Новые данные в conversations.json — запускаю дообучение в фоне...")
                asyncio.create_task(launch_retrain_async())  # ← ✅ не блокирует
        except Exception as e:
            logger.error(f"⚠️ Ошибка проверки времени файла: {e}")
    # === КОНЕЦ АСИНХРОННОГО ЗАПУСКА ===

    # Загружаем модель
    try:
        logger.info("🔁 Загружаю чат-бот...")
        load_start = asyncio.get_event_loop().time()
        ChatBot = import_chatbot()
        new_bot = ChatBot(str(MODEL_PATH), str(DATA_PATH))
        load_time = asyncio.get_event_loop().time() - load_start
        logger.info(f"📦 ChatBot загружен за {load_time:.2f} сек")

        with CHATBOT_LOCK:
            chatbot = new_bot
        logger.info("✅ Чат-бот успешно загружен!")
        try:
            logger.info("🔍 Инициализирую WebSearch...")
            web_search_start = asyncio.get_event_loop().time()
            from src.web_search import WebSearch
            global web_search
            
            # Создаём объект
            web_search = WebSearch()
            
            # Явно вызываем инициализацию драйвера
            logger.info("🚀 Вызываю web_search.init_driver()...")
            web_search.init_driver()
            
            # 🔴 КРИТИЧЕСКАЯ ПРОВЕРКА: убедиться, что драйвер запустился
            if web_search.driver is None:
                logger.critical("❌ init_driver() НЕ УДАЛСЯ (driver = None)!")
                raise RuntimeError("WebSearch: драйвер не инициализировался. Проверь Chrome/undetected_chromedriver.")
            
            web_search_time = asyncio.get_event_loop().time() - web_search_start
            logger.info(f"✅ WebSearch инициализирован за {web_search_time:.2f} сек")
            
            # 🔴 ДОБАВЛЕНО: загрузка кэша при старте (чтобы избежать ошибок в lookup)
            try:
                cache_file = str(BASE_DIR / "data" / "knowledge_cache.json")
                web_search._load_knowledge_cache(cache_file)
                logger.info(f"📚 knowledge_cache загружен ({cache_file})")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки knowledge_cache: {e}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации WebSearch: {e}")
            web_search = None
            logger.warning("⚠️ WebSearch отключён — поиск слов в интернете недоступен")
        if hasattr(chatbot, 'dataset') and chatbot.dataset is not None:
            logger.info(f"📚 Обучено на {len(chatbot.dataset)} примерах")
    except Exception as e:
        logger.critical(f"❌ Ошибка инициализации бота: {e}", exc_info=True)
        raise

    logger.info(f"✅ Lifespan готов за {asyncio.get_event_loop().time() - start_lifespan:.2f} сек")

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
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# === Эндпоинт: /intuition — сводка настроения ===
@app.get("/intuition")
async def intuition_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'intuition'):
        return {"status": "not available", "detail": "Бот не загружен или интуиция отключена"}

    mood_summary = local_bot.intuition.get_mood_summary()
    return {
        "status": "ok",
        "intuition": mood_summary,
        "enabled": local_bot.intuition_enabled,
    }


# === Эндпоинт: /social — сводка социальных способностей ===
@app.get("/social")
async def social_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'social_engine'):
        return {"status": "not available", "detail": "Бот не загружен или социальные способности отключены"}

    social_summary = local_bot.social_engine.get_social_summary()
    return {
        "status": "ok",
        "social": social_summary,
        "enabled": local_bot.social_enabled,
    }


# === Эндпоинт: /cognitive — сводка когнитивных способностей ===
@app.get("/cognitive")
async def cognitive_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'cognitive_engine'):
        return {"status": "not available", "detail": "Бот не загружен или когнитивные способности отключены"}

    cognitive_summary = local_bot.cognitive_engine.get_cognitive_summary()
    return {
        "status": "ok",
        "cognitive": cognitive_summary,
        "enabled": local_bot.cognitive_enabled,
    }


# === Эндпоинт: /eq — сводка эмоционального интеллекта ===
@app.get("/eq")
async def eq_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'eq_engine'):
        return {"status": "not available", "detail": "Бот не загружен или эмоциональный интеллект отключён"}

    eq_summary = local_bot.eq_engine.get_eq_summary()
    return {
        "status": "ok",
        "eq": eq_summary,
        "enabled": local_bot.eq_enabled,
    }


# === Главная страница ===
@app.get("/")
def home():
    return {
        "message": "🎉 С Днём Рождения! ChatBot API работает!",
        "version": app.version,
        "endpoints": ["/predict", "/retrain", "/enrich", "/ws", "/health"],
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
        if v not in ["chat", "world_gen", "narrative", "rpg", "continue"]:
            raise ValueError("mode должен быть 'chat', 'world_gen', 'narrative', 'rpg' или 'continue'")
        return v

# === Эндпоинт: /predict и / — оба работают ===
@app.post("/predict")
@app.post("/")  # Совместимость с Android
async def predict(request: Request):
    start_time = asyncio.get_event_loop().time()
    logger.info(f"📥 Запрос /predict | UA: {request.headers.get('User-Agent', 'unknown')}")

    user_agent = request.headers.get("User-Agent", "")
    if "PantikurBot" not in user_agent:
        logger.warning(f"🚫 Заблокирован User-Agent: {user_agent}")
        raise HTTPException(status_code=403, detail="Доступ запрещён")

    try:
        body = await request.json()
        logger.debug(f"📥 JSON получен ({len(str(body))} байт)")
    except Exception:
        logger.error("❌ Ошибка разбора JSON")
        raise HTTPException(status_code=400, detail="Невалидный JSON")

    try:
        req = ChatRequest(**body)
        logger.info(f"✅ Запрос валидирован | Статус: OK | mode={req.mode}, count={len(req.messages)}")
    except Exception as e:
        logger.error(f"❌ Ошибка валидации: {e}")
        raise HTTPException(status_code=422, detail=f"Ошибка валидации: {str(e)}")

    if not req.messages:
        logger.warning("⚠️ История пуста")
        raise HTTPException(status_code=422, detail="История сообщений пуста")
    if len(req.messages) > 32:
        logger.warning(f"⚠️ Слишком длинная история: {len(req.messages)}")
        raise HTTPException(status_code=422, detail="Слишком длинная история (макс. 32 сообщения)")

    # 🔁 === ДОБАВЛЕНО: Автоматическое определение RPG-режима ===
    def detect_rpg_mode(messages: List[MessageItem]) -> str:
        context_snippet = "\n".join([
            m.message.lower() for m in messages[-2:]
        ])

        rpg_keywords = {
            "hp", "здоровье", "урон", "атака", "защита", "шанс", "пробой",
            "инвентарь", "предмет", "золото", "эксп", " xp ", "lvl", "уровень",
            "локация", "место", "пещера", "лес", "город", "дом", "таверна",
            "враг", "монстр", "гоблин", "орк", "дракон", "скелет", "призрак",
            "шаг", "идти", "бежать", "осмотреться", "взять", "схватить",
            "схватка", "борьба", "драка", "выстрел", "заклинание", "магия",
            "класс", "рыцарь", "маг", "вор", "паладин", "жрец", "некромант"
        }

        if any(kw in context_snippet for kw in rpg_keywords):
            return "rpg"
        
        # Специфичные фразы → narrative/world_gen
        if any(kw in context_snippet for kw in ["создай", "мир", "вселенная"]):
            return "world_gen" if "жанр" in context_snippet else "narrative"

        return "chat"

    # 🔁 Переключение режима: если пришёл chat, но есть RPG-сигналы
    mode = req.mode
    if mode == "chat":
        detected = detect_rpg_mode(req.messages)
        if detected in ["rpg", "world_gen", "narrative"]:
            logger.info(f"➡️ Переключено с 'chat' → '{detected}' (RPG-сигналы)")
            mode = detected
    # === КОНЕЦ RPG-AUTO ===

    # Безопасное получение chatbot
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    local_ws = None
    with WEBSH_LOCK:
        local_ws = web_search

    if local_bot is None:
        logger.error("❌ chatbot не загружен")
        raise HTTPException(status_code=500, detail="Сервис временно недоступен")

    # === Генерация по режимам ===
    try:
        start_gen = asyncio.get_event_loop().time()
        response = ""

        if mode == "narrative":
            logger.info("🔧 Режим: narrative")
            context = "\n".join([
                f"{'Пользователь' if m.is_own else 'Бот'}: {m.message}"
                for m in req.messages
            ])
            prompt_text = textwrap.dedent(f"""
                Ты — писатель-сценарист. Пиши атмосферные сцены в стиле научной фантастики/драмы.
                Отвечай только на русском языке.

                Строгий формат ответа:
                **Локация — Время**
                Описание окружения и действий персонажей.
                «Диалог» — описание действия говорящего.
                *Внутренние мысли в курсиве.*

                Пример стиля:
                **Жилой сектор — Ванная — 22:42**
                Нобука открывает дверь. Пар поднимается из ванны.
                «Даже горячая ванна есть», — улыбается она.
                *Горячая вода. Настоящая.* — думает Сидни.

                История диалога:
                {context}

                Бот:
            """).strip()
            start_subgen = asyncio.get_event_loop().time()
            response = local_bot.generate_response([{"message": prompt_text, "is_own": True}], mode="chat").strip()
            elapsed_sub = asyncio.get_event_loop().time() - start_subgen
            logger.info(f"⏱ narrative: {elapsed_sub:.2f} сек | Длина ответа: {len(response)}")

            if len(response) < 20:
                response = "*Фигура медленно обернулась* 'ты... вернулся... *(внутренне: сердце сжалось)*'"
                logger.warning("⚠️ Слишком короткий ответ → fallback")

        elif mode == "world_gen":
            logger.info("🔧 Режим: world_gen")
            last_msg = req.messages[-1].message
            genre = "Фэнтези"
            tags = ""

            genre_match = re.search(r"Жанр:\s*([^.\n]+)", last_msg, re.IGNORECASE)
            if genre_match:
                genre = genre_match.group(1).strip()

            tags_match = re.search(r"Темы:\s*([^.\n]+)", last_msg, re.IGNORECASE)
            if tags_match:
                tags = tags_match.group(1).strip()

            input_msg = f"Создай мир: {genre}"
            if tags:
                input_msg += f", {tags}"

            start_subgen = asyncio.get_event_loop().time()
            response = local_bot.generate_response([{"message": input_msg, "is_own": True}], mode="world_gen").strip()
            elapsed_sub = asyncio.get_event_loop().time() - start_subgen
            logger.info(f"⏱ world_gen: {elapsed_sub:.2f} сек | Длина ответа: {len(response)}")

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
                logger.warning("⚠️ Неверный формат → fallback")

        elif mode == "rpg":
            logger.info("🔧 Режим: rpg")
            valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
            start_subgen = asyncio.get_event_loop().time()
            response = local_bot.generate_response(valid_msgs, mode="rpg").strip()
            elapsed_sub = asyncio.get_event_loop().time() - start_subgen
            logger.info(f"⏱ rpg: {elapsed_sub:.2f} сек | Длина ответа: {len(response)}")

        elif mode == "continue":
            logger.info("🔧 Режим: continue")
            valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
            start_subgen = asyncio.get_event_loop().time()
            response = local_bot.generate_response(valid_msgs, mode="continue").strip()
            elapsed_sub = asyncio.get_event_loop().time() - start_subgen
            logger.info(f"⏱ continue: {elapsed_sub:.2f} сек | Длина ответа: {len(response)}")

            if not response:
                response = random.choice(["Это важно...", "Ты прав...", "Может быть...", "Интересно..."])
                logger.warning("⚠️ Пустой ответ → fallback")

        else:  # chat (остаток)
            logger.info("🔧 Режим: chat")
            # === ПАРСИНГ КОНТЕКСТА ДЛЯ НОВЫХ СЛОВ (только в режиме chat) ===
            word_to_lookup = None
            lookup_result = None
            if mode == "chat" and local_ws and local_ws.driver is not None:  # ← ДОБАВЛЕНА ПРОВЕРКА
                    # 1. Ищем последнее сообщение пользователя
                    last_user_msg = None
                    for msg in reversed(req.messages):
                        if not msg.is_own:
                            last_user_msg = msg.message
                            break

                    # 2. Если есть сообщение — ищем новое слово
                    if last_user_msg and local_ws and local_ws.driver is not None:  # ← ДОБАВЛЕНА ПРОВЕРКА
                        try:
                            words = local_ws.get_word_from_context(last_user_msg)
                            if words:
                                word_to_lookup = words[0]
                                logger.info(f"🔍 Найдено слово для поиска: '{word_to_lookup}'")
                        except Exception as e:
                            logger.warning(f"⚠️ Ошибка в get_word_from_context: {e}")

                    # 3. Если слово найдено — ищем его значение
                    if word_to_lookup and local_ws and local_ws.driver is not None:  # ← ДОБАВЛЕНА ПРОВЕРКА
                        try:
                            lookup_start = asyncio.get_event_loop().time()
                            knowledge_cache = getattr(local_bot, 'knowledge_cache', None)
                            save_cache_func = None
                            if knowledge_cache and hasattr(local_bot, 'save_knowledge_cache'):
                                save_cache_func = local_bot.save_knowledge_cache

                            definition = local_ws.lookup(
                                word_to_lookup,
                                timeout=2.0,
                                knowledge_cache=knowledge_cache,
                                save_knowledge_cache_func=save_cache_func
                            )
                            if definition:
                                lookup_result = definition
                                logger.info(f"✅ lookup('{word_to_lookup}'): '{definition[:50]}...'")
                        except Exception as e:
                            logger.error(f"❌ Ошибка lookup: {e}")
                # === КОНЕЦ ПАРСИНГА СЛОВ ===

            # === ДОБАВЛЕНО: Вставка определения слова в контекст ===
            if lookup_result:
                # Создаем новый контекст с определением слова
                modified_messages = list(req.messages)
                # Вставляем определение перед последним сообщением пользователя
                modified_messages.insert(-1, MessageItem(message=f"Словарное определение: {lookup_result}", is_own=False))
                logger.info(f"🔍 Вставляю определение в контекст: '{lookup_result[:50]}...'")
                valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in modified_messages]
            else:
                valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]

            start_subgen = asyncio.get_event_loop().time()
            response = local_bot.generate_response(valid_msgs, mode="chat").strip()
            elapsed_sub = asyncio.get_event_loop().time() - start_subgen
            logger.info(f"⏱ chat: {elapsed_sub:.2f} сек | Длина ответа: {len(response)}")

            if not response:
                response = "Я здесь! 🤖"
                logger.warning("⚠️ Пустой ответ → fallback")

        total_elapsed = asyncio.get_event_loop().time() - start_time
        logger.info(f"✅ Ответ сгенерирован за {total_elapsed:.2f} сек | Mode: {mode} | len={len(response)}")
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


# === Эндпоинт: /enrich — сборка данных от GigaChat ===
@app.post("/enrich")
async def enrich_gigachat(request: Request):
    if not GIGACHAT_TOKEN:
        raise HTTPException(status_code=503, detail="GIGACHAT_TOKEN не задан")

    token = request.headers.get("X-Retrain-Token")
    if token != RETRAIN_TOKEN:
        raise HTTPException(status_code=403, detail="Неверный токен")

    try:
        from bot_learns_from_gigachat import generate_self_teaching_dialogs
        logger.info("🤖 Запускаю self-teaching от GigaChat...")
        generate_self_teaching_dialogs(n=3)
        return {"status": "enriched", "detail": "Диалоги добавлены в conversations.json"}
    except Exception as e:
        logger.error(f"❌ Ошибка enrichment: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка enrichment: {e}")


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