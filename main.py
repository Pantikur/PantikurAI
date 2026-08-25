# main.py — ChatBot API (модульная версия)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# === Импорт конфигурации ===
from config import (
    BASE_DIR, WUGLARST_DIR, WUGLARST_SRC_DIR,
    AUTO_BOOK_LEARNING_ENABLED,
    AUTO_RETRAIN_ENABLED,
    AUTO_WEB_SEARCH_ENABLED,
    WHITELISTED_IPS,
    RETRAIN_TOKEN,
    CONVERSATIONS_JSON,
)

# === Импорт сервисов ===
from services.model_loader import load_qwen_model
from services.security import (
    rate_limit_store, rate_limit_lock,
    attack_store, attack_lock,
    blocked_ips, check_rate_limit, is_suspicious_request, is_ip_blocked, block_ip,
)
from services.service_init import (
    init_latislane, init_celesta, init_research_monitor,
    get_latislane, get_celesta, get_research_monitor,
    get_latislane_lock, get_celesta_lock, get_research_monitor_lock,
)
from services.model_init import (
    load_chatbot, init_web_search, reload_model,
    get_chatbot_ref, get_chatbot_lock,
)
from services.background_tasks import (
    start_auto_book_learning, start_auto_retrain, start_auto_web_search,
)
from services.retrain_service import run_retrain

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

# === .env ===
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
    logger.info("✅ .env загружен")
except ImportError:
    logger.warning("⚠️ python-dotenv не установлен")

# === Инициализация сервисов (синхронная, без asyncio) ===
latislane_core = init_latislane()
celesta_core = init_celesta()
research_monitor = init_research_monitor()

# === Wuglarst App ===
WUGLARST_APP = None
try:
    from Wuglarst.server_autonomous import app as wuglarst_app
    WUGLARST_APP = wuglarst_app
    logger.info("✅ Wuglarst app импортирован")
except Exception as e:
    logger.warning(f"⚠️ Wuglarst app не импортирован: {e}")


# === Lifespan ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Загрузка модели
    await load_chatbot()

    # 2. Инициализация WebSearch
    ws_instance = await init_web_search()

    # 3. Фоновые задачи
    await start_auto_book_learning()
    await start_auto_web_search(ws_instance)

    if AUTO_RETRAIN_ENABLED:
        asyncio.create_task(start_auto_retrain())

    # 4. Монитор перезагрузки модели
    async def model_reload_monitor():
        while True:
            await asyncio.sleep(30)
            await reload_model()

    asyncio.create_task(model_reload_monitor())

    # 5. Ретраин при наличии данных
    if CONVERSATIONS_JSON.exists():
        try:
            logger.warning("🎂 Есть данные для обучения — запускаю ретраин в фоне...")
            asyncio.create_task(asyncio.to_thread(run_retrain))
        except Exception as e:
            logger.error(f"⚠️ Ошибка: {e}")

    yield

    logger.info("🛑 Чат-бот остановлен. Хорошего дня! 🎈")


# === FastAPI приложение ===
app = FastAPI(
    title="ChatBot API",
    description="API для Android-приложения PantikurChat",
    version="1.5.0 🎂",
    lifespan=lifespan,
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
    local_bot = get_chatbot_ref()[0]
    return {
        "status": "ok",
        "bot_ready": local_bot is not None,
        "timestamp": datetime.now().isoformat(),
        "blocked_ips": len(blocked_ips),
        "rate_limit_active": True,
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
            "enabled": research_monitor is not None,
            "scientists": ["hanako", "fuyuki", "lucy", "futaba", "shiori", "nobuka", "latislane", "celesta", "akva", "yu"],
        },
    }


# === Подключение роутера ===
from api.router import router as api_router
from api.dependencies import (
    get_chatbot_ref as _get_chatbot_ref,
    get_chatbot_lock as _get_chatbot_lock,
    get_latislane_lock as _get_latislane_lock,
    get_celesta_lock as _get_celesta_lock,
    get_research_monitor_lock as _get_research_monitor_lock,
)

# === Dependency overrides ===
chatbot_lock = get_chatbot_lock()

app.dependency_overrides = {
    _get_chatbot_ref: get_chatbot_ref,
    _get_chatbot_lock: lambda: chatbot_lock,
    _get_latislane_lock: get_latislane_lock,
    _get_celesta_lock: get_celesta_lock,
    _get_research_monitor_lock: get_research_monitor_lock,
}

app.include_router(api_router)


# === Запуск ===
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    logger.info("📌 Сервер готов. Запускаем...")
    uvicorn.run("main:app", host="0.0.0.0", port=port)
