# main.py — ChatBot API (модульная версия)

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import sys
import asyncio
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
import threading

# === Импорт конфигурации ===
from config import (
    BASE_DIR, DATA_PATH, CONVERSATIONS_JSON,
    WUGLARST_DIR, WUGLARST_SRC_DIR,
    AUTO_BOOK_LEARNING_ENABLED, AUTO_BOOK_LEARNING_CYCLE, AUTO_BOOK_MAX_BOOKS,
    AUTO_RETRAIN_ENABLED, AUTO_RETRAIN_INTERVAL, LAST_RETRAIN_FILE, retrain_status,
    RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW,
    WHITELISTED_IPS,
    AUTO_WEB_SEARCH_ENABLED, AUTO_WEB_SEARCH_INTERVAL, AUTO_WEB_SEARCH_BATCH_SIZE,
    AUTO_WEB_SEARCH_MIN_LENGTH, AUTO_WEB_SEARCH_EXTRACT_DEPTH, AUTO_WEB_SEARCH_MAX_NEW_WORDS,
    AUTO_GIRLS_ENABLED, GIRLS_TO_RUN,
    APP_LOG_FILE,
    GIGACHAT_TOKEN, RETRAIN_TOKEN,
    LATISLANE_ENABLED, CELESTA_ENABLED, RESEARCH_MONITOR_ENABLED,
)

# === Импорт сервисов ===
from services.model_loader import load_qwen_model, get_qwen_cache
from services.security import (
    rate_limit_store, rate_limit_lock,
    attack_store, attack_lock,
    blocked_ips, check_rate_limit, is_suspicious_request, is_ip_blocked, block_ip
)

# === Настройка логирования ===
APP_LOG_FILE = os.getenv("APP_LOG_FILE", "logs/app.log")
logging_handlers = [logging.StreamHandler(sys.stdout)]
if APP_LOG_FILE:
    try:
        _log_dir = os.path.dirname(APP_LOG_FILE) or "."
        os.makedirs(_log_dir, exist_ok=True)
        logging_handlers.append(logging.FileHandler(APP_LOG_FILE, encoding="utf-8"))
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=logging_handlers,
)
logger = logging.getLogger("main")

os.makedirs("logs", exist_ok=True)

# === Wuglarst path ===
if WUGLARST_SRC_DIR.exists():
    if str(WUGLARST_DIR) not in sys.path:
        sys.path.insert(0, str(WUGLARST_DIR))
        logger.info(f"✅ Путь added: {WUGLARST_DIR}")
elif WUGLARST_DIR.exists():
    if str(WUGLARST_DIR) not in sys.path:
        sys.path.insert(0, str(WUGLARST_DIR))
        logger.warning(f"⚠️ Использую Wuglarst (а не Wuglarst/src)")
else:
    logger.critical(f"❌ Не найдена директория: {WUGLARST_DIR}")
    raise RuntimeError(f"Не найдена директория: {WUGLARST_DIR}")

# === Wuglarst App ===
WUGLARST_APP = None
try:
    from Wuglarst.server_autonomous import app as wuglarst_app
    WUGLARST_APP = wuglarst_app
    logger.info("✅ Wuglarst app импортирован")
except Exception as e:
    logger.warning(f"⚠️ Wuglarst app не импортирован: {e}")

# === .env ===
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
    logger.info("✅ .env загружен")
except ImportError:
    logger.warning("⚠️ python-dotenv не установлен")

from typing import Any

# === Глобальные переменные ===
chatbot_ref: list[Any] = [None]
CHATBOT_LOCK = threading.RLock()
_qwen_cache_ref: list[Any] = [None]
web_search = None
WEBSH_LOCK = threading.Lock()
LATISLANE_LOCK = threading.Lock()
CELESTA_LOCK = threading.Lock()
RESEARCH_MONITOR_LOCK = threading.Lock()

latislane_core = None
if LATISLANE_ENABLED:
    try:
        sys.path.insert(0, str(BASE_DIR))
        from latislane import LatislaneCore
        latislane_core = LatislaneCore(project_root=str(BASE_DIR), demo_mode=True)
        logger.info("🧬 Latislane инициализирован")
    except Exception as e:
        logger.warning(f"⚠️ Latislane не загружен: {e}")

celesta_core = None
if CELESTA_ENABLED:
    try:
        sys.path.insert(0, str(BASE_DIR))
        from celesta import CelestaCore
        celesta_core = CelestaCore(project_root=str(BASE_DIR), demo_mode=True)
        logger.info("🌹 Celesta инициализирована")
    except Exception as e:
        logger.warning(f"⚠️ Celesta не загружена: {e}")

research_monitor = None
if RESEARCH_MONITOR_ENABLED:
    try:
        sys.path.insert(0, str(BASE_DIR))
        from scientists_network.research_monitor import ResearchMonitor
        research_monitor = ResearchMonitor()
        research_monitor.initialize()
        logger.info("🔬 ResearchMonitor инициализирован")
    except Exception as e:
        logger.warning(f"⚠️ ResearchMonitor не загружен: {e}")


# === Lifespan ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Автообучение из книг
    if AUTO_BOOK_LEARNING_ENABLED:
        logger.info(f"📚 Автообучение из книг: ВКЛЮЧЕНО")
        async def start_auto_book_learning():
            try:
                from utils.auto_book_learning import AutoBookLearning
                await asyncio.sleep(10)
                controller = AutoBookLearning(
                    cycle_minutes=AUTO_BOOK_LEARNING_CYCLE,
                    max_books_per_cycle=AUTO_BOOK_MAX_BOOKS,
                    topics_per_cycle=2
                )
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, controller.run_continuous)
            except Exception as e:
                logger.error(f"❌ Ошибка автообучения из книг: {e}")
        asyncio.create_task(start_auto_book_learning())

    # Автозапуск девочек
    if AUTO_GIRLS_ENABLED:
        logger.info(f"🔮 Автозапуск девочек: ВКЛЮЧЕНО ({len(GIRLS_TO_RUN)})")
        def start_girls_orchestrator():
            time.sleep(15)
            import subprocess
            orchestrator_path = Path(__file__).parent / "orchestrator_v3.py"
            if orchestrator_path.exists():
                subprocess.Popen(
                    [sys.executable, str(orchestrator_path)],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, bufsize=1,
                )
        asyncio.create_task(asyncio.to_thread(start_girls_orchestrator))

    # Авто-обучение модели
    if AUTO_RETRAIN_ENABLED:
        logger.info(f"🧠 Авто-обучение модели: ВКЛЮЧЕНО")
        async def start_auto_retrain():
            async def retrain_cycle():
                try:
                    import subprocess as sp
                    retrain_status["status"] = "running"
                    result = sp.run(
                        [sys.executable, "retrain.py", "--generate", "0"],
                        capture_output=True, text=True, timeout=7200
                    )
                    if result.returncode == 0:
                        retrain_status.update({
                            "last_retrain": datetime.now().isoformat(),
                            "last_retrain_success": True,
                            "total_retrains": retrain_status.get("total_retrains", 0) + 1,
                            "status": "success"
                        })
                        with open(LAST_RETRAIN_FILE, "w") as f:
                            json.dump(retrain_status, f)
                    else:
                        retrain_status["status"] = "error"
                        logger.error(f"❌ Ошибка авто-обучения: {result.stderr[:500]}")
                except Exception as e:
                    retrain_status["status"] = "error"
                    logger.error(f"❌ Ошибка авто-обучения: {e}")
            
            await asyncio.sleep(300)
            await retrain_cycle()
            while True:
                await asyncio.sleep(AUTO_RETRAIN_INTERVAL)
                await retrain_cycle()
        asyncio.create_task(start_auto_retrain())

    # Монитор перезагрузки модели
    async def model_reload_monitor():
        signal_file = BASE_DIR / "data" / ".model_needs_reload"
        while True:
            await asyncio.sleep(30)
            if signal_file.exists():
                logger.info("📡 Сигнал от Наото: перезагрузка модели...")
                try:
                    _qwen_cache_ref[0] = None
                    qwen_model = load_qwen_model()
                    with CHATBOT_LOCK:
                        chatbot_ref[0] = qwen_model
                    logger.info("✅ Модель перезагружена!")
                    signal_file.unlink()
                except Exception as e:
                    logger.error(f"❌ Перезагрузка не удалась: {e}")
    asyncio.create_task(model_reload_monitor())

    # Загрузка модели в фоне
    async def load_chatbot_background():
        logger.info("🔁 Загружаю Qwen2.5-3B (в фоне)...")
        qwen_model = await asyncio.to_thread(load_qwen_model)
        if qwen_model is None:
            logger.warning("⚠️ Модель не загружена")
            return
        _qwen_cache_ref[0] = qwen_model
        with CHATBOT_LOCK:
            chatbot_ref[0] = qwen_model
        logger.info("✅ Qwen2.5-3B успешно загружен!")

    asyncio.create_task(load_chatbot_background())

    # WebSearch
    async def init_websearch_background():
        try:
            from src.web_search import WebSearch
            def _init():
                ws = WebSearch()
                ws.init_driver()
                return ws
            ws_result = await asyncio.to_thread(_init)
            if ws_result is not None and ws_result.driver is not None:
                with WEBSH_LOCK:
                    global web_search
                    web_search = ws_result
                logger.info("✅ WebSearch инициализирован")
                if AUTO_WEB_SEARCH_ENABLED:
                    async def start_auto_web_search():
                        try:
                            from utils.auto_web_search import AutoWebSearch
                            await asyncio.sleep(30)
                            controller = AutoWebSearch(
                                interval_seconds=AUTO_WEB_SEARCH_INTERVAL,
                                batch_size=AUTO_WEB_SEARCH_BATCH_SIZE,
                                min_word_length=AUTO_WEB_SEARCH_MIN_LENGTH,
                                extract_depth=AUTO_WEB_SEARCH_EXTRACT_DEPTH,
                                max_new_words_per_def=AUTO_WEB_SEARCH_MAX_NEW_WORDS,
                                project_root=str(BASE_DIR)
                            )
                            with WEBSH_LOCK:
                                controller.web_search = web_search
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, controller.run_continuous)
                        except Exception as e:
                            logger.error(f"❌ Ошибка автопоиска слов: {e}")
                    asyncio.create_task(start_auto_web_search())
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации WebSearch: {e}")
    asyncio.create_task(init_websearch_background())

    # Ретраин при наличии данных
    if CONVERSATIONS_JSON.exists():
        try:
            logger.warning("🎂 Есть данные для обучения — запускаю ретраин в фоне...")
            asyncio.create_task(asyncio.to_thread(run_retrain_sync))
        except Exception as e:
            logger.error(f"⚠️ Ошибка: {e}")

    yield

    logger.info("🛑 Чат-бот остановлен. Хорошего дня! 🎈")


def run_retrain_sync():
    """Запуск retrain.py в фоне."""
    from services.model_loader import load_qwen_model
    if not RETRAIN_TOKEN:
        logger.error("❌ RETRAIN_TOKEN не задан")
        return
    if not CHATBOT_LOCK.acquire(blocking=False):
        logger.warning("🔄 Ретраин уже запущен")
        return
    logger.info("🎂 Запускаю ретраин...")
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "retrain.py"], cwd=str(BASE_DIR),
            capture_output=True, text=True, timeout=600
        )
        if result.returncode == 0:
            logger.info("🎉 Ретраин завершён!")
            try:
                _qwen_cache_ref[0] = None
                qwen_model = load_qwen_model()
                with CHATBOT_LOCK:
                    chatbot_ref[0] = qwen_model
            except Exception as e:
                logger.error(f"❌ Не удалось перезагрузить модель: {e}")
        else:
            logger.error(f"❌ Ошибка ретраина: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("⏰ Превышен лимит времени (10 мин)")
    except Exception as e:
        logger.error(f"💥 Ошибка запуска: {e}")
    finally:
        CHATBOT_LOCK.release()


# === FastAPI приложение ===
app = FastAPI(
    title="ChatBot API",
    description="API для Android-приложения PantikurChat",
    version="1.5.0 🎂",
    lifespan=lifespan
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === МОНТИРОВАНИЕ WUGLARST ===
if WUGLARST_APP:
    app.mount("/wuglarst", WUGLARST_APP)

# === Middleware: Безопасность ===
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    
    if request.url.path in ("/health", "/ping"):
        return await call_next(request)
    
    if client_ip in WHITELISTED_IPS:
        return await call_next(request)
    
    is_blocked, msg = is_ip_blocked(client_ip)
    if is_blocked:
        return JSONResponse(status_code=403, content={"detail": msg})
    
    is_suspicious, reason = is_suspicious_request(request)
    if is_suspicious:
        block_ip(client_ip, reason)
        return JSONResponse(status_code=403, content={"detail": "Доступ запрещён: подозрительная активность"})
    
    if request.url.path not in ("/health", "/ping"):
        if not check_rate_limit(client_ip):
            return JSONResponse(status_code=429, content={"detail": "Слишком много запросов"})
    
    return await call_next(request)


# === Health Check ===
@app.get("/health")
async def health_check():
    local_bot = None
    with CHATBOT_LOCK:
        local_bot = chatbot_ref[0]
    return {
        "status": "ok",
        "bot_ready": local_bot is not None,
        "girls_enabled": AUTO_GIRLS_ENABLED,
        "girls_count": len(GIRLS_TO_RUN),
        "timestamp": datetime.now().isoformat(),
        "blocked_ips": len(blocked_ips),
        "rate_limit_active": RATE_LIMIT_REQUESTS > 0
    }

@app.get("/ping")
async def ping():
    return {"status": "ok"}


# === Главная страница ===
@app.get("/")
def home():
    return {
        "message": "🎉 С Днём Рождения! ChatBot API работает!",
        "version": app.version,
        "endpoints": ["/predict", "/chat", "/retrain", "/enrich", "/health", "/docs"],
        "world_engine": {"enabled": True, "description": "Система управления мирами"},
        "people_generator": {"enabled": True, "description": "Генерация людей, семей, организаций"},
        "kotlin_assistant": {"enabled": True, "description": "AI-помощник для Kotlin"},
        "research_monitor": {
            "enabled": True,
            "scientists": ["hanako", "fuyuki", "lucy", "futaba", "shiori", "nobuka", "latislane", "celesta", "akva", "yu"],
        }
    }


# === Подключение роутера ===
from api.router import router as api_router
from api.dependencies import (
    get_chatbot_ref, get_CHATBOT_LOCK,
    get_LATISLANE_LOCK, get_CELESTA_LOCK, get_RESEARCH_MONITOR_LOCK,
    get_latislane_core, get_celesta_core, get_research_monitor
)

# === Регистрация dependency overrides ===
app.dependency_overrides = {
    get_chatbot_ref: lambda: chatbot_ref,
    get_CHATBOT_LOCK: lambda: CHATBOT_LOCK,
    get_LATISLANE_LOCK: lambda: LATISLANE_LOCK,
    get_CELESTA_LOCK: lambda: CELESTA_LOCK,
    get_RESEARCH_MONITOR_LOCK: lambda: RESEARCH_MONITOR_LOCK,
    get_latislane_core: lambda: latislane_core,
    get_celesta_core: lambda: celesta_core,
    get_research_monitor: lambda: research_monitor,
}

app.include_router(api_router)


# === Запуск ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info("📌 Сервер готов. Запускаем...")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
