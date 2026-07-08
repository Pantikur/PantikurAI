# main.py — ChatBot API

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Dict, Tuple, Any, Optional
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
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timedelta

# === Импорт модуля параметров человека ===
from utils.human_params import HumanParams, HumanParamsDetector

# === Автономное обучение из книг (запуск в фоне) ===
AUTO_BOOK_LEARNING_ENABLED = os.getenv("AUTO_BOOK_LEARNING", "true").lower() in ("true", "1", "yes")
AUTO_BOOK_LEARNING_CYCLE = int(os.getenv("AUTO_BOOK_LEARNING_CYCLE", "10"))  # минут
AUTO_BOOK_MAX_BOOKS = int(os.getenv("AUTO_BOOK_MAX_BOOKS", "5"))  # книг за цикл

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

# === Rate Limiting и безопасность ===
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))  # запросов в минуту
RATE_LIMIT_WINDOW = 60  # секунд

# Подозрительные User-Agents (сканеры уязвимостей)
SUSPICIOUS_UA_PATTERNS = [
    "python-requests", "curl/", "wget/", "scrapy", "nikto", "nmap",
    "sqlmap", "masscan", "zgrab", "gobuster", "dirbuster", "wfuzz",
    "nuclei", "burp", "acunetix", "nessus", "openvas"
]

# Подозрительные пути (сканирование уязвимостей)
SUSPICIOUS_PATHS = [
    ".env", ".git", ".svn", ".hg", "wp-admin", "wp-content", "phpinfo",
    "phpmyadmin", "adminer", "shell", "cmd", "exec", "eval", "backup",
    ".sql", ".dump", ".pem", ".key", ".htaccess", ".htpasswd", "config.php",
    "web.config", ".aws", ".azure", ".docker", "kubernetes", "terraform"
]

# Хранилище rate limiting: IP -> список временных меток
rate_limit_store: Dict[str, List[float]] = defaultdict(list)
rate_limit_lock = threading.Lock()

# Чёрный список IP (автоматически пополняется)
blocked_ips: Dict[str, datetime] = {}  # IP -> время блокировки
BLOCK_DURATION = timedelta(hours=24)  # Длительность блокировки

# Белый список IP (минует все проверки безопасности)
WHITELISTED_IPS_RAW = os.getenv("WHITELISTED_IPS", "127.0.0.1,::1,172.18.0.2")
WHITELISTED_IPS = set(ip.strip() for ip in WHITELISTED_IPS_RAW.split(","))


def check_rate_limit(client_ip: str) -> bool:
    """
    Проверяет rate limit для IP.
    :return: True если запрос разрешён, False если превышен лимит
    """
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    with rate_limit_lock:
        # Очищаем старые записи
        rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if t > window_start]
        
        # Проверяем лимит
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            return False
        
        # Добавляем текущую метку
        rate_limit_store[client_ip].append(now)
        return True


def is_suspicious_request(request: Request) -> Tuple[bool, str]:
    """
    Проверяет запрос на подозрительную активность.
    :return: (is_suspicious, reason)
    """
    ua = request.headers.get("User-Agent", "").lower()
    path = request.url.path.lower()
    
    # Проверка User-Agent
    for pattern in SUSPICIOUS_UA_PATTERNS:
        if pattern in ua:
            return True, f"Suspicious UA: {pattern}"
    
    # Проверка пути
    for suspicious in SUSPICIOUS_PATHS:
        if suspicious in path:
            return True, f"Suspicious path: {suspicious}"
    
    return False, ""

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
    logger.warning("⚠️ GIGACHAT_TOKEN не задан — ретраин без данных от GigaChat")
# === КОНЕЦ GIGACHAT_TOKEN ===

# === Глобальная переменная бота и блокировка ===
chatbot = None
CHATBOT_LOCK = threading.RLock()  # Защита при доступе и перезагрузке
    # === Глобальная переменная WebSearch ===
web_search = None
WEBSH_LOCK = threading.Lock()  # Защита при доступе к web_search

# === Автопоиск новых слов (запуск в фоне) ===
AUTO_WEB_SEARCH_ENABLED = os.getenv("AUTO_WEB_SEARCH", "true").lower() in ("true", "1", "yes")
AUTO_WEB_SEARCH_INTERVAL = int(os.getenv("AUTO_WEB_SEARCH_INTERVAL", "3600"))  # секунд (по умолчанию 1 час)
AUTO_WEB_SEARCH_BATCH_SIZE = int(os.getenv("AUTO_WEB_SEARCH_BATCH_SIZE", "10"))  # слов за цикл
AUTO_WEB_SEARCH_MIN_LENGTH = int(os.getenv("AUTO_WEB_SEARCH_MIN_LENGTH", "2"))  # минимальная длина слова
AUTO_WEB_SEARCH_EXTRACT_DEPTH = int(os.getenv("AUTO_WEB_SEARCH_EXTRACT_DEPTH", "1"))  # глубина извлечения слов
AUTO_WEB_SEARCH_MAX_NEW_WORDS = int(os.getenv("AUTO_WEB_SEARCH_MAX_NEW_WORDS", "10"))  # макс новых слов из определения

# === Импорт ChatBot с резервом ===
def import_chatbot():
    global chatbot
    try:
        from src.chatbot import ChatBot  # type: ignore
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
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Не удалось создать spec для {chatbot_path}")
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
    
    # === ЗАПУСК АВТОНОМНОГО ОБУЧЕНИЯ ИЗ КНИГ ===
    if AUTO_BOOK_LEARNING_ENABLED:
        logger.info(f"📚 Автономное обучение из книг: ВКЛЮЧЕНО")
        logger.info(f"   ⏱️ Цикл: {AUTO_BOOK_LEARNING_CYCLE} минут")
        logger.info(f"   📚 Книг за цикл: {AUTO_BOOK_MAX_BOOKS}")
        logger.info(f"   🌐 Источник: Author.Today (русскоязычные)")

        async def start_auto_book_learning():
            """Запускает автообучение в фоне"""
            try:
                from utils.auto_book_learning import AutoBookLearning
                
                # Небольшая задержка перед стартом
                await asyncio.sleep(10)
                
                controller = AutoBookLearning(
                    cycle_minutes=AUTO_BOOK_LEARNING_CYCLE,
                    max_books_per_cycle=AUTO_BOOK_MAX_BOOKS,
                    topics_per_cycle=2
                )
                
                # Запускаем в отдельном потоке
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, controller.run_continuous)
                
            except Exception as e:
                logger.error(f"❌ Ошибка автообучения из книг: {e}")
        
        # Запускаем фоновую задачу
        asyncio.create_task(start_auto_book_learning())
    else:
        logger.info("📚 Автономное обучение из книг: ОТКЛЮЧЕНО")
    # === КОНЕЦ АВТОНОМНОГО ОБУЧЕНИЯ ===
    

    start_lifespan = asyncio.get_event_loop().time()
    logger.info("🔄 Старт lifespan...")

    # Проверяем обязательные файлы — НЕ бросаем ошибку, чтобы не блокировать старт
    # Файлы могут подмонтироваться позже (volumes в Docker)
    missing = []
    for path, name in [(DATA_PATH, "токенизатор"), (MODEL_PATH, "модель")]:
        if not path.exists():
            logger.warning(f"⚠️ Файл не найден: {name} → {path} (будет попытка загрузки позже)")
            missing.append(name)
    
    if missing:
        logger.warning(f"⚠️ Некоторые файлы отсутствуют при старте: {', '.join(missing)}")
        logger.info("ℹ️ Приложение запустится, но бот может не работать пока файлы не появятся")
    
    

    logger.info(f"📁 Все необходимые файлы найдены за {asyncio.get_event_loop().time() - start_lifespan:.2f} сек")

    # === Асинхронный запуск ретраина при старте (не блокирует запуск) ===
    async def launch_retrain_async():
        await asyncio.to_thread(run_retrain_sync)

    if CONVERSATIONS_JSON.exists():
        try:
            model_mtime = MODEL_PATH.stat().st_mtime
            data_mtime = CONVERSATIONS_JSON.stat().st_mtime
            if data_mtime > model_mtime:
                logger.warning("🎂 Новые данные в conversations.json — запускаю ретраин в фоне...")
                asyncio.create_task(launch_retrain_async())  # ← ✅ не блокирует
        except Exception as e:
            logger.error(f"⚠️ Ошибка проверки времени файла: {e}")
    # === КОНЕЦ АСИНХРОННОГО ЗАПУСКА ===

    # === Фоновая загрузка ChatBot + WebSearch (не блокирует запуск сервера) ===
    async def load_chatbot_background():
        global chatbot, web_search
        try:
            logger.info("🔁 Загружаю чат-бот (в фоне)...")
            load_start = asyncio.get_event_loop().time()
            ChatBot = import_chatbot()
            new_bot = await asyncio.to_thread(ChatBot, str(MODEL_PATH), str(DATA_PATH))
            load_time = asyncio.get_event_loop().time() - load_start
            logger.info(f"📦 ChatBot загружен за {load_time:.2f} сек")

            with CHATBOT_LOCK:
                chatbot = new_bot
            logger.info("✅ Чат-бот успешно загружен!")

            if hasattr(chatbot, 'dataset') and chatbot.dataset is not None:  # type: ignore[reportAttributeAccessIssue]
                logger.info(f"📚 Обучено на {len(chatbot.dataset)} примерах")  # type: ignore[reportAttributeAccessIssue]

            # === WebSearch инициализация (в фоне, не блокирует) ===
            try:
                logger.info("🔍 Инициализирую WebSearch (в фоне)...")
                web_search_start = asyncio.get_event_loop().time()
                from src.web_search import WebSearch  # type: ignore

                def _init_websearch():
                    ws = WebSearch()
                    ws.init_driver()
                    return ws

                ws_result = await asyncio.to_thread(_init_websearch)

                if ws_result is None or ws_result.driver is None:
                    logger.warning("⚠️ init_driver() вернул driver=None — WebSearch отключён")
                else:
                    with WEBSH_LOCK:
                        web_search = ws_result

                    # Загрузка кэша
                    try:
                        cache_file = str(BASE_DIR / "data" / "knowledge_cache.json")
                        web_search._load_knowledge_cache(cache_file)
                        logger.info(f"📚 knowledge_cache загружен ({cache_file})")
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка загрузки knowledge_cache: {e}")

                    web_search_time = asyncio.get_event_loop().time() - web_search_start
                    logger.info(f"✅ WebSearch инициализирован за {web_search_time:.2f} сек")

                    # === ЗАПУСК АВТОНОМНОГО ПОИСКА СЛОВ ===
                    if AUTO_WEB_SEARCH_ENABLED:
                        logger.info(f"🔍 Автопоиск слов: ВКЛЮЧЕНО")
                        logger.info(f"   ⏱️ Интервал: {AUTO_WEB_SEARCH_INTERVAL // 60} минут")
                        logger.info(f"   📝 Слов за цикл: {AUTO_WEB_SEARCH_BATCH_SIZE}")

                        async def start_auto_web_search():
                            """Запускает автопоиск слов в фоне"""
                            try:
                                from utils.auto_web_search import AutoWebSearch
                                
                                # Небольшая задержка перед стартом (ждем полной загрузки)
                                await asyncio.sleep(30)
                                
                                controller = AutoWebSearch(
                                    interval_seconds=AUTO_WEB_SEARCH_INTERVAL,
                                    batch_size=AUTO_WEB_SEARCH_BATCH_SIZE,
                                    min_word_length=AUTO_WEB_SEARCH_MIN_LENGTH,
                                    extract_depth=AUTO_WEB_SEARCH_EXTRACT_DEPTH,
                                    max_new_words_per_def=AUTO_WEB_SEARCH_MAX_NEW_WORDS,
                                    project_root=str(BASE_DIR)
                                )
                                
                                # Подключаем web_search (если инициализирован)
                                with WEBSH_LOCK:
                                    controller.web_search = web_search
                                
                                # Запускаем в отдельном потоке
                                loop = asyncio.get_event_loop()
                                await loop.run_in_executor(None, controller.run_continuous)
                                
                            except Exception as e:
                                logger.error(f"❌ Ошибка автопоиска слов: {e}")
                        
                        # Запускаем фоновую задачу
                        asyncio.create_task(start_auto_web_search())
                    else:
                        logger.info("🔍 Автопоиск слов: ОТКЛЮЧЁН")

            except Exception as e:
                logger.error(f"❌ Ошибка инициализации WebSearch: {e}")
                with WEBSH_LOCK:
                    web_search = None
                logger.warning("⚠️ WebSearch отключён — поиск слов в интернете недоступен")

        except Exception as e:
            logger.critical(f"❌ Ошибка инициализации бота: {e}", exc_info=True)
            logger.warning("⚠️ Бот не загружен — API будет работать, но ответы недоступны")
            logger.info("🔄 Запуск фоновой задачи повторной загрузки бота...")
            try:
                asyncio.create_task(auto_reload_chatbot_loop())
            except Exception as retry_err:
                logger.error(f"❌ Не удалось запустить задачу авто-загрузки: {retry_err}")

    # Запускаем загрузку в фоне — сервер стартует немедленно
    asyncio.create_task(load_chatbot_background())

    logger.info(f"✅ Lifespan готов за {asyncio.get_event_loop().time() - start_lifespan:.2f} сек (бот грузится в фоне)")

    yield

    # Очистка при остановке
    logger.info("🛑 Чат-бот остановлен. Хорошего дня! 🎈")


async def auto_reload_chatbot_loop():
    """Фоновая задача: периодически проверяет файлы и загружает бота, когда они появятся."""
    global chatbot
    check_interval = 10  # секунд
    max_attempts = 60  # максимум 10 минут (60 * 10с)
    
    for attempt in range(1, max_attempts + 1):
        await asyncio.sleep(check_interval)
        
        # Проверяем наличие файлов
        if not MODEL_PATH.exists():
            logger.debug(f"🔄 Авто-загрузка (попытка {attempt}/{max_attempts}): модель ещё не найдена")
            continue
        if not DATA_PATH.exists():
            logger.debug(f"🔄 Авто-загрузка (попытка {attempt}/{max_attempts}): токенизатор ещё не найден")
            continue
        
        logger.info(f"🔄 Авто-загрузка (попытка {attempt}/{max_attempts}): файлы найдены, пробуем загрузить бота...")
        try:
            load_start = asyncio.get_event_loop().time()
            ChatBot = import_chatbot()
            new_bot = ChatBot(str(MODEL_PATH), str(DATA_PATH))
            load_time = asyncio.get_event_loop().time() - load_start
            with CHATBOT_LOCK:
                chatbot = new_bot
            logger.info(f"✅ Бот успешно загружен авто-загрузкой за {load_time:.2f} сек!")
            if hasattr(new_bot, 'dataset') and new_bot.dataset is not None:  # type: ignore[reportAttributeAccessIssue]
                logger.info(f"📚 Обучено на {len(new_bot.dataset)} примерах")  # type: ignore[reportAttributeAccessIssue]
            return  # Успешно загружено, выходим
        except Exception as e:
            logger.error(f"❌ Авто-загрузка бота не удалась (попытка {attempt}): {e}")
    
    logger.warning("⚠️ Авто-загрузка бота: исчерпано максимальное число попыток")


# === FastAPI приложение ===
app = FastAPI(
    title="ChatBot API",
    description="API для Android-приложения PantikurChat",
    version="1.5.0 🎂",
    lifespan=lifespan
)


# === Middleware: Rate Limiting + Защита от сканирования ===
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    
    # Health check полностью минует security-проверки (нужен для Docker/Timeweb)
    if request.url.path == "/health":
        response = await call_next(request)
        return response
    
    # Проверка на заблокированные IP
    if client_ip in WHITELISTED_IPS:
        response = await call_next(request)
        return response
    
    if client_ip in blocked_ips:
        block_time = blocked_ips[client_ip]
        if datetime.now() < block_time + BLOCK_DURATION:
            remaining = (block_time + BLOCK_DURATION - datetime.now()).seconds // 60
            logger.warning(f"🚫 Заблокирован IP {client_ip} (осталось {remaining} мин)")
            return JSONResponse(
                status_code=403,
                content={"detail": f"IP заблокирован. Осталось минут: {remaining}"}
            )
        else:
            # Снимаем блокировку
            del blocked_ips[client_ip]
            logger.info(f"✅ Снята блокировка с IP {client_ip}")
    
    # Проверка на подозрительные запросы (сканирование уязвимостей)
    is_suspicious, reason = is_suspicious_request(request)
    if is_suspicious:
        # Блокируем IP на 24 часа
        blocked_ips[client_ip] = datetime.now()
        logger.warning(f"🚫 Блокировка IP {client_ip}: {reason}")
        return JSONResponse(
            status_code=403,
            content={"detail": "Доступ запрещён: подозрительная активность"}
        )
    
    # Rate limiting (не применяем к health check)
    if request.url.path != "/health":
        if not check_rate_limit(client_ip):
            logger.warning(f"⚠️ Rate limit превышен для IP {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Слишком много запросов. Повторите через минуту."}
            )
    
    # Продолжаем обработку
    response = await call_next(request)
    return response


# === Health Check с деталями ===
@app.get("/health")
async def health_check():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot
    return {
        "status": "ok",
        "bot_ready": local_bot is not None,
        "timestamp": datetime.now().isoformat(),
        "blocked_ips": len(blocked_ips),
        "rate_limit_active": RATE_LIMIT_REQUESTS > 0
    }


# === Endpoint: мониторинг безопасности ===
@app.get("/security")
async def security_status():
    """Показывает статус безопасности: заблокированные IP, rate limit."""
    now = datetime.now()
    active_blocks = {}
    for ip, block_time in blocked_ips.items():
        expires = block_time + BLOCK_DURATION
        if now < expires:
            remaining = (expires - now).seconds // 60
            active_blocks[ip] = f"{remaining} мин"
    
    return {
        "status": "ok",
        "rate_limit": {
            "requests_per_minute": RATE_LIMIT_REQUESTS,
            "window_seconds": RATE_LIMIT_WINDOW
        },
        "blocked_ips": {
            "count": len(active_blocks),
            "active_blocks": active_blocks
        },
        "suspicious_patterns": {
            "ua_patterns": len(SUSPICIOUS_UA_PATTERNS),
            "path_patterns": len(SUSPICIOUS_PATHS)
        }
    }


# === Endpoint: разблокировать IP (админский) ===
@app.post("/security/unblock/{ip}")
async def unblock_ip(ip: str, request: Request):
    """Разблокирует IP адрес."""
    token = request.headers.get("X-Retrain-Token")
    if token != RETRAIN_TOKEN:
        raise HTTPException(status_code=403, detail="Неверный токен")

    if ip in blocked_ips:
        del blocked_ips[ip]
        logger.info(f"✅ IP {ip} разблокирован администратором")
        return {"status": "ok", "detail": f"IP {ip} разблокирован"}
    else:
        return {"status": "ok", "detail": f"IP {ip} не был заблокирован"}


# === Эндпоинт: /intuition — сводка настроения ===
@app.get("/intuition")
async def intuition_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'intuition'):
        return {"status": "not available", "detail": "Бот не загружен или интуиция отключена"}

    mood_summary = local_bot.intuition.get_mood_summary()  # type: ignore[reportAttributeAccessIssue]
    return {
        "status": "ok",
        "intuition": mood_summary,
        "enabled": local_bot.intuition_enabled,  # type: ignore[reportAttributeAccessIssue]
    }


# === Эндпоинт: /social — сводка социальных способностей ===
@app.get("/social")
async def social_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'social_engine'):
        return {"status": "not available", "detail": "Бот не загружен или социальные способности отключены"}

    social_summary = local_bot.social_engine.get_social_summary()  # type: ignore[reportAttributeAccessIssue]
    return {
        "status": "ok",
        "social": social_summary,
        "enabled": local_bot.social_enabled,  # type: ignore[reportAttributeAccessIssue]
    }


# === Эндпоинт: /cognitive — сводка когнитивных способностей ===
@app.get("/cognitive")
async def cognitive_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'cognitive_engine'):
        return {"status": "not available", "detail": "Бот не загружен или когнитивные способности отключены"}

    cognitive_summary = local_bot.cognitive_engine.get_cognitive_summary()  # type: ignore[reportAttributeAccessIssue]
    return {
        "status": "ok",
        "cognitive": cognitive_summary,
        "enabled": local_bot.cognitive_enabled,  # type: ignore[reportAttributeAccessIssue]
    }


# === Эндпоинт: /eq — сводка эмоционального интеллекта ===
@app.get("/eq")
async def eq_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'eq_engine'):
        return {"status": "not available", "detail": "Бот не загружен или эмоциональный интеллект отключён"}

    eq_summary = local_bot.eq_engine.get_eq_summary()  # type: ignore[reportAttributeAccessIssue]
    return {
        "status": "ok",
        "eq": eq_summary,
        "enabled": local_bot.eq_enabled,  # type: ignore[reportAttributeAccessIssue]
    }


# === Эндпоинт: /physiology — сводка физиологических способностей ===
@app.get("/physiology")
async def physiology_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'phys_engine'):
        return {"status": "not available", "detail": "Бот не загружен или физиологические способности отключены"}

    phys_summary = local_bot.phys_engine.get_physiology_summary()  # type: ignore[reportAttributeAccessIssue]
    return {
        "status": "ok",
        "physiology": phys_summary,
        "enabled": local_bot.phys_enabled,  # type: ignore[reportAttributeAccessIssue]
    }


# === Эндпоинт: /special — сводка специальных когнитивных способностей ===
@app.get("/special")
async def special_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'special_cognitive_engine'):
        return {"status": "not available", "detail": "Бот не загружен или специальные способности отключены"}

    special_summary = local_bot.special_cognitive_engine.get_special_cognitive_summary()  # type: ignore[reportAttributeAccessIssue]
    return {
        "status": "ok",
        "special": special_summary,
        "enabled": local_bot.special_cognitive_enabled,  # type: ignore[reportAttributeAccessIssue]
    }


# === Эндпоинт: /professions — сводка по профессиям ===
@app.get("/professions")
async def professions_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'profession_engine'):
        return {"status": "not available", "detail": "Бот не загружен или анализ профессий отключён"}

    profession_summary = local_bot.profession_engine.get_profession_summary()  # type: ignore[reportAttributeAccessIssue]
    return {
        "status": "ok",
        "professions": profession_summary,
        "enabled": local_bot.professions_enabled,  # type: ignore[reportAttributeAccessIssue]
    }


# === Эндпоинт: /imagination — сводка активного воображения ===
@app.get("/imagination")
async def imagination_status():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None or not hasattr(local_bot, 'imagination_engine'):
        return {"status": "not available", "detail": "Бот не загружен или воображение отключено"}

    imagination_summary = local_bot.imagination_engine.get_imagination_summary()  # type: ignore[reportAttributeAccessIssue]
    return {
        "status": "ok",
        "imagination": imagination_summary,
        "enabled": local_bot.imagination_enabled,  # type: ignore[reportAttributeAccessIssue]
    }


# ========================
# WorldEngine Endpoints
# ========================

# === Эндпоинт: /world/create — создать мир ===
@app.post("/world/create")
async def world_create(request: Request):
    """Создаёт новый мир"""
    try:
        body = await request.json()
        genre = body.get("genre", "Фэнтези")
        tag = body.get("tag", "магия")
    except Exception:
        raise HTTPException(status_code=400, detail="Невалидный JSON")

    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        raise HTTPException(status_code=503, detail="WorldEngine не доступен")

    try:
        result = local_bot.create_world(genre, tag)
        return {"status": "ok", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/create-from-books — создать мир из книг ===
@app.post("/world/create-from-books")
async def world_create_from_books(request: Request):
    """Создаёт новый мир на основе прочитанных книг"""
    try:
        body = await request.json()
        genre = body.get("genre")  # Опционально
        tag = body.get("tag")  # Опционально
        book_titles = body.get("book_titles")  # Список названий книг (опционально)
    except Exception:
        raise HTTPException(status_code=400, detail="Невалидный JSON")

    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        raise HTTPException(status_code=503, detail="WorldEngine не доступен")

    try:
        result = local_bot.create_world_from_books(genre, tag, book_titles)
        return {"status": "ok", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /worlds — список всех миров ===
@app.get("/worlds")
async def worlds_list():
    """Возвращает список всех миров"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = local_bot.get_all_worlds()
        return {"status": "ok", "worlds": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/{name} — информация о мире ===
@app.get("/world/{world_name}")
async def world_info(world_name: str):
    """Возвращает информацию о мире"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = local_bot.get_world_info(world_name)
        return {"status": "ok", "info": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/{name}/event — генерация события ===
@app.post("/world/{world_name}/event")
async def world_generate_event(world_name: str):
    """Генерирует событие в мире"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = local_bot.generate_event(world_name)
        return {"status": "ok", "event": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/{name}/events — последние события ===
@app.get("/world/{world_name}/events")
async def world_get_events(world_name: str, limit: int = 10):
    """Возвращает последние события мира"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = local_bot.get_world_events(world_name, limit)
        return {"status": "ok", "events": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/{name}/consistency — проверка консистентности ===
@app.get("/world/{world_name}/consistency")
async def world_check_consistency(world_name: str):
    """Проверяет консистентность лора мира"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = local_bot.check_consistency(world_name)
        return {"status": "ok", "consistency": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/{name}/npc/{npc_name} — информация о NPC ===
@app.get("/world/{world_name}/npc/{npc_name}")
async def world_get_npc(world_name: str, npc_name: str):
    """Возвращает информацию о NPC"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = local_bot.get_npc_info(world_name, npc_name)
        return {"status": "ok", "npc": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/start-cycle — запуск фонового цикла ===
@app.post("/world/start-cycle")
async def world_start_cycle():
    """Запускает фоновый цикл развития миров"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = await local_bot.start_background_cycle()
        return {"status": "ok", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/stop-cycle — остановка фонового цикла ===
@app.post("/world/stop-cycle")
async def world_stop_cycle():
    """Останавливает фоновый цикл развития миров"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = local_bot.stop_background_cycle()
        return {"status": "ok", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/status — статус WorldEngine ===
@app.get("/world/status")
async def world_status():
    """Возвращает статус всех систем WorldEngine"""
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot

    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")

    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}

    try:
        result = local_bot.get_world_status()
        return {"status": "ok", "status": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# People Generator Endpoints
# ========================

# === Эндпоинт: /generate/person — сгенерировать человека ===
@app.post("/generate/person")
async def generate_person(request: Request):
    """Генерирует одного человека на основе знаний"""
    try:
        from utils.world_people_generator import PeopleGenerator
        
        body = await request.json() if request.method == "POST" else {}
        age_min = body.get("age_min", 18)
        age_max = body.get("age_max", 40)
        gender = body.get("gender")  # "мужской" или "женский"
        archetype = body.get("archetype")
        
        generator = PeopleGenerator()
        person = generator.generate_person(
            age_range=(age_min, age_max),
            gender=gender,
            archetype=archetype
        )
        
        return {"status": "ok", "person": person.to_dict()}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации человека: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /generate/family — сгенерировать семью ===
@app.post("/generate/family")
async def generate_family(request: Request):
    """Генерирует семью на основе знаний"""
    try:
        from utils.world_people_generator import PeopleGenerator
        
        body = await request.json() if request.method == "POST" else {}
        size = body.get("size", 4)
        region = body.get("region")
        
        generator = PeopleGenerator()
        family = generator.generate_family(size=size, region=region)
        
        return {"status": "ok", "family": family.to_dict()}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации семьи: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /generate/organization — сгенерировать организацию ===
@app.post("/generate/organization")
async def generate_organization(request: Request):
    """Генерирует организацию на основе знаний"""
    try:
        from utils.world_people_generator import PeopleGenerator
        
        body = await request.json() if request.method == "POST" else {}
        org_type = body.get("type")  # company, government, ngo, club, criminal
        size = body.get("size")  # small, medium, large, corporation
        
        generator = PeopleGenerator()
        organization = generator.generate_organization(type=org_type, size=size)
        
        return {"status": "ok", "organization": organization.to_dict()}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации организации: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /generate/country — сгенерировать страну ===
@app.post("/generate/country")
async def generate_country(request: Request):
    """Генерирует страну на основе знаний"""
    try:
        from utils.world_people_generator import PeopleGenerator
        
        body = await request.json() if request.method == "POST" else {}
        pop_min = body.get("population_min", 1000000)
        pop_max = body.get("population_max", 100000000)
        
        generator = PeopleGenerator()
        country = generator.generate_country(population_range=(pop_min, pop_max))
        
        return {"status": "ok", "country": country.to_dict()}
    except Exception as e:
        logger.error(f"❌ Ошибка генерации страны: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /generate/world-population — сгенерировать популяцию мира ===
@app.post("/generate/world-population")
async def generate_world_population(request: Request):
    """Генерирует полную популяцию мира: люди, семьи, организации, страны"""
    try:
        from utils.world_people_generator import PeopleGenerator
        
        body = await request.json() if request.method == "POST" else {}
        num_people = body.get("people", 50)
        num_families = body.get("families", 10)
        num_organizations = body.get("organizations", 5)
        num_countries = body.get("countries", 3)
        
        generator = PeopleGenerator()
        world_data = generator.generate_world_population(
            num_people=num_people,
            num_families=num_families,
            num_organizations=num_organizations,
            num_countries=num_countries
        )
        
        # Возвращаем только статистику, чтобы не перегружать ответ
        return {
            "status": "ok",
            "stats": world_data["stats"],
            "output_file": f"data/generated_worlds/world_population_*.json"
        }
    except Exception as e:
        logger.error(f"❌ Ошибка генерации популяции: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /world/{name}/add-people — добавить людей в мир ===
@app.post("/world/{world_name}/add-people")
async def world_add_people(world_name: str, request: Request):
    """Добавляет сгенерированных людей в существующий мир"""
    try:
        from utils.world_people_generator import WorldEngineIntegration
        
        body = await request.json() if request.method == "POST" else {}
        num_people = body.get("num", 10)
        
        integration = WorldEngineIntegration()
        success = integration.add_people_to_world(world_name, num_people=num_people)
        
        if success:
            return {"status": "ok", "detail": f"Добавлено {num_people} персонажей в мир {world_name}"}
        else:
            raise HTTPException(status_code=404, detail=f"Мир {world_name} не найден")
    except Exception as e:
        logger.error(f"❌ Ошибка добавления людей в мир: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Kotlin Assistant Endpoints
# ========================

# === Модели запросов для Kotlin Assistant ===
class KotlinGenerateRequest(BaseModel):
    """Запрос на генерацию Kotlin-кода"""
    description: str
    template_type: str | None = None  # activity, fragment, viewmodel, repository, dataclass, etc.
    package_name: str = "com.example.app"
    class_name: str = "MyClass"
    additional_context: str | None = None


class KotlinEditRequest(BaseModel):
    """Запрос на редактирование Kotlin-кода"""
    existing_code: str
    instructions: str
    file_path: str | None = None


class KotlinAnalyzeRequest(BaseModel):
    """Запрос на анализ Kotlin-кода"""
    code: str
    file_path: str | None = None


class KotlinRefactorRequest(BaseModel):
    """Запрос на рефакторинг Kotlin-кода"""
    code: str
    refactor_type: str  # extract_function, rename, simplify, modernize
    file_path: str | None = None


class KotlinAutocompleteRequest(BaseModel):
    """Запрос на автодополнение Kotlin-кода"""
    code_prefix: str
    context: str | None = None


class KotlinContextRequest(BaseModel):
    """Запрос на сохранение контекста файла"""
    file_path: str
    code: str


# === Эндпоинт: /kotlin/generate — генерация кода ===
@app.post("/kotlin/generate")
async def kotlin_generate(request: KotlinGenerateRequest):
    """
    Генерирует Kotlin-код по описанию.
    
    Поддерживаемые шаблоны:
    - activity, fragment, viewmodel, repository
    - dataclass, retrofit_api, room_dao
    - singleton, coroutine_worker, compose_ui
    - compose_viewmodel, dependency_injection, navigation_graph
    """
    try:
        from utils.kotlin_assistant import KotlinAssistant
        
        assistant = KotlinAssistant(project_root=str(BASE_DIR))
        result = assistant.generate_code(  # type: ignore[reportAttributeAccessIssue]
            description=request.description,
            template_type=request.template_type,
            package_name=request.package_name,
            class_name=request.class_name,
            additional_context=request.additional_context
        )
        
        logger.info(f"✅ Kotlin генерация: {request.class_name} ({request.template_type or 'custom'})")
        return {"status": "ok", **result}
    
    except Exception as e:
        logger.error(f"❌ Ошибка генерации Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin/edit — редактирование кода ===
@app.post("/kotlin/edit")
async def kotlin_edit(request: KotlinEditRequest):
    """
    Редактирует существующий Kotlin-код по инструкции.
    
    Примеры инструкций:
    - "Добавь комментарий к классу"
    - "Добавь импорт lifecycleScope"
    - "Добавь функцию loadData()"
    - "Удали все TODO комментарии"
    """
    try:
        from utils.kotlin_assistant import KotlinAssistant
        
        assistant = KotlinAssistant(project_root=str(BASE_DIR))
        result = assistant.edit_code(  # type: ignore[reportAttributeAccessIssue]
            existing_code=request.existing_code,
            instructions=request.instructions,
            file_path=request.file_path
        )
        
        logger.info(f"✅ Kotlin редактирование: {len(request.existing_code)} символов")
        return {"status": "ok", **result}
    
    except Exception as e:
        logger.error(f"❌ Ошибка редактирования Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin/analyze — анализ кода ===
@app.post("/kotlin/analyze")
async def kotlin_analyze(request: KotlinAnalyzeRequest):
    """
    Анализирует Kotlin-код на ошибки и проблемы.
    
    Возвращает:
    - errors: список ошибок синтаксиса
    - warnings: предупреждения стиля
    - suggestions: предложения по улучшению
    - metrics: метрики кода (строки, классы, функции, сложность)
    """
    try:
        from utils.kotlin_assistant import KotlinAssistant
        
        assistant = KotlinAssistant(project_root=str(BASE_DIR))
        result = assistant.analyze_code(  # type: ignore[reportAttributeAccessIssue]
            code=request.code,
            file_path=request.file_path
        )
        
        logger.info(f"✅ Kotlin анализ: {result['metrics'].get('lines', 0)} строк, {len(result['errors'])} ошибок")
        return {"status": "ok", **result}
    
    except Exception as e:
        logger.error(f"❌ Ошибка анализа Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin/refactor — рефакторинг кода ===
@app.post("/kotlin/refactor")
async def kotlin_refactor(request: KotlinRefactorRequest):
    """
    Выполняет рефакторинг Kotlin-кода.
    
    Типы рефакторинга:
    - extract_function: извлечение функции
    - rename: переименование
    - simplify: упрощение кода
    - modernize: модернизация (устаревшие конструкции)
    """
    try:
        from utils.kotlin_assistant import KotlinAssistant
        
        assistant = KotlinAssistant(project_root=str(BASE_DIR))
        result = assistant.refactor_code(  # type: ignore[reportAttributeAccessIssue]
            code=request.code,
            refactor_type=request.refactor_type,
            file_path=request.file_path
        )
        
        logger.info(f"✅ Kotlin рефакторинг: {request.refactor_type}")
        return {"status": "ok", **result}
    
    except Exception as e:
        logger.error(f"❌ Ошибка рефакторинга Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin/autocomplete — автодополнение ===
@app.post("/kotlin/autocomplete")
async def kotlin_autocomplete(request: KotlinAutocompleteRequest):
    """
    Автодополнение Kotlin-кода.
    
    Возвращает список вариантов продолжения кода
    на основе префикса и контекста.
    """
    try:
        from utils.kotlin_assistant import KotlinAssistant
        
        assistant = KotlinAssistant(project_root=str(BASE_DIR))
        result = assistant.autocomplete(  # type: ignore[reportAttributeAccessIssue]
            code_prefix=request.code_prefix,
            context=request.context
        )
        
        logger.info(f"✅ Kotlin автодополнение: {len(result['suggestions'])} вариантов")
        return {"status": "ok", **result}
    
    except Exception as e:
        logger.error(f"❌ Ошибка автодополнения Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Глобальный инстанс Kotlin Assistant для контекста ===
_kotlin_assistant_instance: Optional[Any] = None


def get_kotlin_assistant():
    """Получает или создаёт инстанс KotlinAssistant."""
    global _kotlin_assistant_instance
    if _kotlin_assistant_instance is None:
        from utils.kotlin_assistant import KotlinAssistant
        _kotlin_assistant_instance = KotlinAssistant(project_root=str(BASE_DIR))
    return _kotlin_assistant_instance
        

# === Эндпоинт: /kotlin/context/save — сохранить контекст ===
@app.post("/kotlin/context/save")
async def kotlin_context_save(request: KotlinContextRequest):
    """
    Сохраняет контекст файла для последующего использования.
    
    Полезно при редактировании нескольких связанных файлов.
    """
    try:
        assistant = get_kotlin_assistant()
        assistant.store_context(  # type: ignore[reportAttributeAccessIssue]
            file_path=request.file_path,
            code=request.code
        )
        
        logger.info(f"✅ Kotlin контекст сохранён: {request.file_path}")
        return {"status": "ok", "detail": f"Контекст сохранён: {request.file_path}"}
    
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения контекста: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin/context/get — получить контекст ===
@app.get("/kotlin/context/get/{file_path:path}")
async def kotlin_context_get(file_path: str):
    """
    Получает сохранённый контекст файла.
    
    file_path должен быть URL-encoded.
    """
    try:
        assistant = get_kotlin_assistant()
        code = assistant.get_context(file_path)  # type: ignore[reportAttributeAccessIssue]
        
        if code:
            logger.info(f"✅ Kotlin контекст получен: {file_path}")
            return {"status": "ok", "file_path": file_path, "code": code}
        else:
            return {"status": "not_found", "detail": f"Контекст не найден: {file_path}"}
    
    except Exception as e:
        logger.error(f"❌ Ошибка получения контекста: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin/context/clear — очистить контекст ===
@app.post("/kotlin/context/clear")
async def kotlin_context_clear():
    """
    Очищает всё хранилище контекста.
    """
    try:
        assistant = get_kotlin_assistant()
        assistant.clear_context()  # type: ignore[reportAttributeAccessIssue]
        
        logger.info("✅ Kotlin контекст очищен")
        return {"status": "ok", "detail": "Контекст очищен"}
    
    except Exception as e:
        logger.error(f"❌ Ошибка очистки контекста: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin/templates — список шаблонов ===
@app.get("/kotlin/templates")
async def kotlin_templates():
    """
    Возвращает список доступных шаблонов Kotlin.
    """
    try:
        from utils.kotlin_assistant import KotlinAssistant
        
        assistant = KotlinAssistant(project_root=str(BASE_DIR))
        templates = list(assistant.templates.keys())  # type: ignore[reportAttributeAccessIssue]
        
        return {
            "status": "ok",
            "templates": templates,
            "description": {
                "activity": "Android Activity",
                "fragment": "Android Fragment",
                "viewmodel": "Android ViewModel",
                "repository": "Repository pattern",
                "dataclass": "Data class",
                "retrofit_api": "Retrofit API interface",
                "room_dao": "Room DAO interface",
                "singleton": "Singleton object",
                "coroutine_worker": "CoroutineWorker",
                "compose_ui": "Jetpack Compose UI",
                "compose_viewmodel": "Compose ViewModel",
                "dependency_injection": "Koin DI module",
                "navigation_graph": "Navigation Compose"
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Ошибка получения шаблонов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin/explain — объяснение кода ===
@app.post("/kotlin/explain")
async def kotlin_explain(request: KotlinAnalyzeRequest):
    """
    Объясняет Kotlin-код простым языком.
    
    Возвращает подробное объяснение:
    - Что делает код
    - Как работают ключевые части
    - Какие паттерны используются
    """
    try:
        from utils.kotlin_assistant import KotlinAssistant
        
        assistant = KotlinAssistant(project_root=str(BASE_DIR))
        result = assistant.explain_code(  # type: ignore[reportAttributeAccessIssue]
            code=request.code,
            file_path=request.file_path
        )
        
        logger.info(f"✅ Kotlin объяснение: {result.get('lines', 0)} строк")
        return {"status": "ok", **result}
    
    except Exception as e:
        logger.error(f"❌ Ошибка объяснения Kotlin: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# App Generator Endpoints
# ========================

class AppGenerateRequest(BaseModel):
    """Запрос на генерацию Android-приложения"""
    app_name: str
    app_type: str  # todo, notes, gallery, weather, chat, custom
    package_name: str = "com.example.app"
    features: List[str] = []  # auth, offline, api, database, etc.


# === Эндпоинт: /app/generate — генерация приложения ===
@app.post("/app/generate")
async def app_generate(request: AppGenerateRequest):
    """
    Генерирует полноценное Android-приложение.
    
    Поддерживаемые типы:
    - todo: Todo List (список задач)
    - notes: Заметки
    - gallery: Галерея изображений
    - weather: Погода
    - chat: Чат
    - custom: Пользовательский
    
    Возвращает:
    - files: словарь с кодом всех файлов
    - description: описание приложения
    """
    try:
        from utils.kotlin_assistant import KotlinAssistant
        
        assistant = KotlinAssistant(project_root=str(BASE_DIR))
        result = assistant.generate_app(  # type: ignore[reportAttributeAccessIssue]
            app_name=request.app_name,
            app_type=request.app_type,
            package_name=request.package_name,
            features=request.features
        )
        
        logger.info(f"✅ Приложение '{request.app_name}' ({request.app_type}) сгенерировано")
        return {"status": "ok", **result}
    
    except Exception as e:
        logger.error(f"❌ Ошибка генерации приложения: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /app/templates — список шаблонов приложений ===
@app.get("/app/templates")
async def app_templates():
    """
    Возвращает список доступных шаблонов приложений.
    """
    return {
        "status": "ok",
        "templates": [
            {"type": "todo", "name": "Todo List", "description": "Список задач с отметками"},
            {"type": "notes", "name": "Notes", "description": "Заметки с Rich Text"},
            {"type": "gallery", "name": "Gallery", "description": "Галерея изображений"},
            {"type": "weather", "name": "Weather", "description": "Прогноз погоды"},
            {"type": "chat", "name": "Chat", "description": "Мессенджер"},
            {"type": "custom", "name": "Custom", "description": "Пользовательский шаблон"}
        ]
    }


# === Эндпоинт: /kotlin-v2/generate — генерация кода (V2) ===
@app.post("/kotlin-v2/generate")
async def kotlin_v2_generate(request: KotlinGenerateRequest):
    """
    Генерирует Kotlin-код (улучшенная версия V2).
    
    Особенности V2:
    - Умное кэширование
    - 20+ расширенных шаблонов
    - Улучшенная AI генерация
    - Статистика использования
    """
    try:
        from utils.kotlin_assistant_v2 import KotlinAssistantV2
        
        assistant = KotlinAssistantV2(project_root=str(BASE_DIR))
        result = assistant.generate_code(  # type: ignore[reportAttributeAccessIssue]
            description=request.description,
            template_type=request.template_type,
            package_name=request.package_name,
            class_name=request.class_name,
            additional_context=request.additional_context
        )
        
        logger.info(f"✅ Kotlin V2 генерация: {request.class_name} ({request.template_type or 'custom'})")
        return {"status": "ok", **result}
    
    except Exception as e:
        logger.error(f"❌ Ошибка генерации Kotlin V2: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin-v2/statistics — статистика ===
@app.get("/kotlin-v2/statistics")
async def kotlin_v2_statistics():
    """
    Возвращает статистику использования Kotlin Assistant V2.
    """
    try:
        from utils.kotlin_assistant_v2 import KotlinAssistantV2
        
        # Создаём временный инстанс для получения статистики
        assistant = KotlinAssistantV2(project_root=str(BASE_DIR))
        stats = assistant.get_statistics()  # type: ignore[reportAttributeAccessIssue]
        
        return {"status": "ok", "statistics": stats}
    
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /kotlin-v2/cache/clear — очистить кэш ===
@app.post("/kotlin-v2/cache/clear")
async def kotlin_v2_cache_clear():
    """
    Очищает кэш Kotlin Assistant V2.
    """
    try:
        from utils.kotlin_assistant_v2 import KotlinAssistantV2
        
        assistant = KotlinAssistantV2(project_root=str(BASE_DIR))
        assistant.clear_cache()  # type: ignore[reportAttributeAccessIssue]
        
        logger.info("✅ Kotlin V2 кэш очищен")
        return {"status": "ok", "detail": "Кэш очищен"}
    
    except Exception as e:
        logger.error(f"❌ Ошибка очистки кэша: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === Главная страница ===
@app.get("/")
def home():
    return {
        "message": "🎉 С Днём Рождения! ChatBot API работает!",
        "version": app.version,
            "endpoints": [
                "/predict", "/", "/chat",
                "/retrain", "/enrich",
                "/ws", "/health",
            "/world/create", "/worlds", "/world/{name}",
            "/world/{name}/event", "/world/{name}/events",
            "/world/{name}/consistency", "/world/{name}/npc/{npc_name}",
            "/world/start-cycle", "/world/stop-cycle", "/world/status",
            "/generate/person", "/generate/family", "/generate/organization",
            "/generate/country", "/generate/world-population",
            "/world/{name}/add-people",
            "/kotlin/generate", "/kotlin/edit", "/kotlin/analyze",
            "/kotlin/refactor", "/kotlin/autocomplete", "/kotlin/templates",
            "/docs"
        ],
        "world_engine": {
            "enabled": True,
            "description": "Полная система управления мирами: создание, события, NPC, лор, фоновый цикл",
            "endpoints": [
                "POST /world/create - Создать мир",
                "POST /world/create-from-books - Создать мир из книг",
                "GET /worlds - Список всех миров",
                "GET /world/{name} - Информация о мире",
                "POST /world/{name}/event - Генерировать событие",
                "GET /world/{name}/events - Последние события",
                "GET /world/{name}/consistency - Проверка лора",
                "GET /world/{name}/npc/{npc_name} - Информация о NPC",
                "POST /world/start-cycle - Запуск фонового цикла",
                "POST /world/stop-cycle - Остановка фонового цикла",
                "GET /world/status - Статус WorldEngine"
            ]
        },
        "people_generator": {
            "enabled": True,
            "description": "Генерация людей, семей, организаций и стран на основе 8 файлов знаний",
            "knowledge_files": [
                "human_adolescence.md",
                "human_early_development.md",
                "human_emerging_adulthood.md",
                "human_late_adolescence.md",
                "human_middle_childhood.md",
                "human_24_years.md",
                "human_daily_life.md",
                "human_daily_routine.md"
            ],
            "endpoints": [
                "POST /generate/person - Сгенерировать человека",
                "POST /generate/family - Сгенерировать семью",
                "POST /generate/organization - Сгенерировать организацию",
                "POST /generate/country - Сгенерировать страну",
                "POST /generate/world-population - Сгенерировать популяцию мира",
                "POST /world/{name}/add-people - Добавить людей в мир"
            ]
        },
        "kotlin_assistant": {
            "enabled": True,
            "description": "AI-помощник для генерации, редактирования и анализа Kotlin-кода. Интеграция с Android Studio.",
            "features": [
                "Генерация кода по описанию (12+ шаблонов)",
                "Редактирование кода по инструкции",
                "Анализ ошибок и стиля кода",
                "Рефакторинг (extract, rename, simplify, modernize)",
                "Автодополнение кода",
                "Управление контекстом файлов"
            ],
            "templates": [
                "activity", "fragment", "viewmodel", "repository",
                "dataclass", "retrofit_api", "room_dao", "singleton",
                "coroutine_worker", "compose_ui", "compose_viewmodel",
                "dependency_injection", "navigation_graph"
            ],
            "endpoints": [
                "POST /kotlin/generate - Генерация кода",
                "POST /kotlin/edit - Редактирование кода",
                "POST /kotlin/analyze - Анализ кода",
                "POST /kotlin/refactor - Рефакторинг",
                "POST /kotlin/explain - Объяснение кода",
                "POST /kotlin/autocomplete - Автодополнение",
                "GET /kotlin/templates - Список шаблонов",
                "POST /kotlin/context/save - Сохранить контекст",
                "GET /kotlin/context/get/{path} - Получить контекст",
                "POST /kotlin/context/clear - Очистить контекст"
            ],
            "android_studio_integration": {
                "description": "Используйте Retrofit для подключения к API из Android Studio",
                "example_dependency": "implementation 'com.squareup.retrofit2:retrofit:2.9.0'",
                "base_url": "http://your-server:8000/"
            }
        }
    }


# === Модели запроса ===
class MessageItem(BaseModel):
    message: str
    is_own: bool
    gender: str | None = None  # "мальчик" | "девочка" — необязательное поле
    skin_tone: str | None = None  # "светлая" | "смуглая" | "темная" — необязательное поле
    hair_color: str | None = None  # "блондин" | "рыжая" | "каштановая" | "чёрная" | "натуральная" | "розовый" | "голубой" | "фиолетовый" | "зеленый" | "радужный" | "разноцветный" | "пепельный" | "крашеный"
    body_shape: str | None = None  # "стройное" | "спортивное" | "мускулистое" | "пышное" | "хрупкое" | "среднее" — необязательное поле
    penis_size: str | None = None  # "маленький" | "средний" | "большой" | "огромный" — необязательное поле (только для мальчиков)
    penis_thickness: str | None = None  # "тонкий" | "средний" | "толстый" | "очень толстый" — необязательное поле (только для мальчиков)
    penis_shape: str | None = None  # "прямой" | "изогнутый вверх" | "изогнутый вниз" | "стреловидный" | "булавовидный" | "округлый" — необязательное поле (только для мальчиков)
    female_anatomy_shape: str | None = None  # "маленькая" | "средняя" | "пышная" | "симметричная" | "асимметричная" | "чувствительная" — необязательное поле (только для девочек)
    female_fluid: str | None = None  # "умеренное" | "обильное" | "минимальное" | "прозрачное" | "молочное" | "вязкое" — необязательное поле (только для девочек)

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
        if v not in ["chat", "world_gen", "narrative", "rpg", "continue", "world"]:
            raise ValueError("mode должен быть 'chat', 'world_gen', 'narrative', 'rpg', 'continue' или 'world'")
        return v

# === Эндпоинт: /predict и / — оба работают ===
@app.post("/predict")
@app.post("/")  # Совместимость с Android
@app.post("/chat")  # Алиас для Android Studio плагина
async def predict(request: Request):
    start_time = asyncio.get_event_loop().time()
    logger.info(f"📥 Запрос /predict | UA: {request.headers.get('User-Agent', 'unknown')}")

    user_agent = request.headers.get("User-Agent", "")
    # Разрешаем PantikurBot или стандартные браузерные UA (для тестирования)
    # Middleware уже отфильтровал подозрительные UA
    if "PantikurBot" not in user_agent and "Mozilla" not in user_agent:
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
        
        # Специфичные фразы → narrative/world_gen/world
        if any(kw in context_snippet for kw in ["создай", "мир", "вселенная"]):
            return "world" if ("жанр" in context_snippet or "тег" in context_snippet) else ("world_gen" if "жанр" in context_snippet else "narrative")

        return "chat"

    # 🔁 Переключение режима: если пришёл chat, но есть RPG-сигналы
    mode = req.mode
    if mode == "chat":
        detected = detect_rpg_mode(req.messages)
        if detected in ["rpg", "world_gen", "narrative"]:
            logger.info(f"➡️ Переключено с 'chat' → '{detected}' (RPG-сигналы)")
            mode = detected
    
    # === КОНЕЦ RPG-AUTO ===

    # === ОПРЕДЕЛЕНИЕ ВСЕХ ПАРАМЕТРОВ ЧЕЛОВЕКА (используем модуль human_params) ===
    # Преобразуем MessageItem в Dict для совместимости с HumanParamsDetector
    messages_dicts = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
    params = HumanParamsDetector.detect_all_params(messages_dicts)
    
    logger.info(f"👤 Параметры: пол={params.gender}, возраст={params.age}({params.age_years}), "
                f"кожа={params.skin_tone}, волосы={params.hair_color}, тело={params.body_shape}, "
                f"грудь={params.breast_size}, ягодицы={params.glute_shape}")
    # === КОНЕЦ ОПРЕДЕЛЕНИЯ ПАРАМЕТРОВ ===

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

        if mode == "world":
            logger.info("🔧 Режим: world (создание мира)")
            # Создаём мир через WorldEngine
            if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
                raise HTTPException(status_code=503, detail="WorldEngine не доступен")
            
            # Парсим жанр из сообщения
            genre = "Фэнтези"
            tag = ""
            
            genre_match = re.search(r"Жанр[:\s]+([^.\n]+)", req.messages[-1].message, re.IGNORECASE)
            if genre_match:
                genre = genre_match.group(1).strip()
            else:
                genre = req.messages[-1].message.strip()[:50]
            
            tag_match = re.search(r"Тег[:\s]+([^.\n]+)", req.messages[-1].message, re.IGNORECASE)
            if tag_match:
                tag = tag_match.group(1).strip()
            
            result = local_bot.create_world(genre, tag)
            response = json.dumps({"response": result}, ensure_ascii=False)
            logger.info(f"📚 world: {result}")

        elif mode == "narrative":
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
            # Передаём все параметры человека в бот
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
            response = local_bot.generate_response([{"message": prompt_text, "is_own": True}], mode="chat").strip()
            elapsed_sub = asyncio.get_event_loop().time() - start_subgen
            logger.info(f"⏱ narrative: {elapsed_sub:.2f} сек | Длина ответа: {len(response)}")

            if len(response) < 20:
                response = "*Фигура медленно обернулась* 'ты... вернулся... *(внутренне: сердце сжалось)*'"
                logger.warning("⚠️ Слишком короткий ответ → fallback")

        elif mode == "world_gen":
            logger.info("🔧 Режим: world_gen")
            last_msg = req.messages[-1].message
            
            # Парсим жанр и тег
            genre = "Фэнтези"
            tag = ""
            
            genre_match = re.search(r"Жанр[:\s]+([^.;\n]+)", last_msg, re.IGNORECASE)
            if genre_match:
                genre = genre_match.group(1).strip()
            else:
                genre = last_msg.strip()[:50]
            
            tag_match = re.search(r"Тег[иаеs]*[:\s]+([^.;\n]+)", last_msg, re.IGNORECASE)
            if tag_match:
                tag = tag_match.group(1).strip()
            
            # === ГЕНЕРАЦИЯ МИРА ЧЕРЕЗ БАЗУ ЗНАНИЙ (не шаблоны!) ===
            try:
                # Вызываем метод бота, который использует все источники знаний
                response = local_bot.generate_response(
                    [{"message": last_msg, "is_own": True}],
                    mode="world_gen"
                )
                # Ответ приходит в формате JSON
                parsed = json.loads(response)
                response = parsed.get("world", parsed.get("response", ""))
                logger.info(f"📚 world_gen: сгенерирован мир '{genre}' (тег: '{tag}')")
            except ImportError as e:
                logger.warning(f"⚠️ world_gen_knowledge не найден: {e} → fallback")
                response = (
                    f"Название: {random.choice(['Тёмный', 'Сияющий', 'Забытый', 'Вечный'])} {random.choice(['Хранитель', 'Звёзд', 'Теней', 'Мечты'])}\n\n"
                    f"Общее описание мира: В мире {genre} {tag if tag else 'магия'} стала основой существования.\n\n"
                    f"Локальное описание: Ты стоишь на краю обрыва перед кристальным городом.\n\n"
                    f"Сюжетная вводная: Ты не помнишь, как сюда попал, но чувствуешь: здесь начинается приключение."
                )
            except json.JSONDecodeError:
                logger.warning("⚠️ world_gen: ответ не JSON → fallback")
                response = f"В мире {genre} {tag if tag else 'что-то необычное'} происходит магия. Ты стоишь перед городом..."
            except Exception as e:
                logger.error(f"❌ Ошибка генерации мира: {e}")
                response = f"В мире {genre} {tag if tag else 'неизвестные силы'} творят чудеса. Опиши, что ты видишь..."
            
            start_subgen = asyncio.get_event_loop().time()
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
            elapsed_sub = asyncio.get_event_loop().time() - start_subgen
            logger.info(f"⏱ world_gen: {elapsed_sub:.2f} сек | Длина ответа: {len(response)}")

        elif mode == "rpg":
            logger.info("🔧 Режим: rpg")
            valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
            start_subgen = asyncio.get_event_loop().time()
            response = local_bot.generate_response(valid_msgs, mode="rpg").strip()
            elapsed_sub = asyncio.get_event_loop().time() - start_subgen
            logger.info(f"⏱ rpg: {elapsed_sub:.2f} сек | Длина ответа: {len(response)}")

        elif mode == "continue":
            logger.info("🔧 Режим: continue")
            valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
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
                            if knowledge_cache and hasattr(local_bot, 'save_knowledge_cache'):  # type: ignore[reportAttributeAccessIssue]
                                save_cache_func = local_bot.save_knowledge_cache  # type: ignore[reportAttributeAccessIssue]

                            definition = local_ws.lookup(
                                word_to_lookup,
                                timeout=2.0,
                                knowledge_cache=knowledge_cache,
                                save_knowledge_cache_func=save_cache_func
                            )
                            if definition:
                                lookup_result = definition
                                if isinstance(definition, str):
                                    logger.info(f"✅ lookup('{word_to_lookup}'): '{definition[:50]}...'")
                                else:
                                    logger.info(f"✅ lookup('{word_to_lookup}'): '{str(definition)[:50]}...'")
                        except Exception as e:
                            logger.error(f"❌ Ошибка lookup: {e}")
                # === КОНЕЦ ПАРСИНГА СЛОВ ===

            # === ДОБАВЛЕНО: Вставка определения слова в контекст ===
            if lookup_result:
                # Создаем новый контекст с определением слова
                modified_messages = list(req.messages)
                # Вставляем определение перед последним сообщением пользователя
                result_text = str(lookup_result)
                modified_messages.insert(-1, MessageItem(message=f"Словарное определение: {result_text}", is_own=False))
                logger.info(f"🔍 Вставляю определение в контекст: '{result_text[:50]}...'")
                valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in modified_messages]
            else:
                valid_msgs = [{"message": m.message, "is_own": m.is_own} for m in req.messages]

            start_subgen = asyncio.get_event_loop().time()
            HumanParamsDetector.apply_params_to_bot(local_bot, params)
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


# === Ретраин (защищённое) ===
RETRAIN_LOCK = threading.Lock()

# НЕ выкидываем ошибку здесь — иначе сломается сборка Docker
RETRAIN_TOKEN = os.getenv("RETRAIN_TOKEN")
if not RETRAIN_TOKEN:
    logger.warning("⚠️ Переменная RETRAIN_TOKEN не задана в .env — /retrain будет отключён")


def run_retrain_sync():
    """Запуск retrain.py в фоне с блокировкой"""
    global chatbot
    if not RETRAIN_TOKEN:
        logger.error("❌ RETRAIN_TOKEN не задан — ретраин недоступен")
        return

    if not RETRAIN_LOCK.acquire(blocking=False):
        logger.warning("🔄 Ретраин уже запущено")
        return

    logger.info("🎂 Запускаю ретраин (обучение с нуля)...")
    try:
        result = subprocess.run(
            [sys.executable, "retrain.py"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            logger.info("🎉 Ретраин завершён успешно!")
            # Перезагрузка модели
            try:
                ChatBot = import_chatbot()
                new_bot = ChatBot(str(MODEL_PATH), str(DATA_PATH))
                with CHATBOT_LOCK:
                    chatbot = new_bot
                logger.info("🔁 Модель перезагружена после обучения")
            except Exception as e:
                logger.error(f"❌ Не удалось перезагрузить модель: {e}")
        else:
            logger.error(f"❌ Ошибка ретраина: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("⏰ Превышен лимит времени (10 мин)")
    except Exception as e:
        logger.error(f"💥 Ошибка запуска: {e}")
    finally:
        RETRAIN_LOCK.release()


@app.post("/retrain")
async def trigger_retrain(request: Request, background_tasks: BackgroundTasks):
    if not RETRAIN_TOKEN:
        raise HTTPException(status_code=503, detail="Ретраин отключен (нет RETRAIN_TOKEN)")

    token = request.headers.get("X-Retrain-Token")
    if token != RETRAIN_TOKEN:
        raise HTTPException(status_code=403, detail="Неверный токен 🎂")

    logger.info("🔧 Запрос на ретраин получен — ставим в фон")
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