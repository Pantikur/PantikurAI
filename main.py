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

# === Авто-обучение модели (ретраин) ===
AUTO_RETRAIN_ENABLED = os.getenv("AUTO_RETRAIN", "true").lower() in ("true", "1", "yes")
AUTO_RETRAIN_INTERVAL = int(os.getenv("AUTO_RETRAIN_INTERVAL", "86400"))  # секунд (по умолчанию 1 день = 86400)
LAST_RETRAIN_FILE = "data/.last_retrain_timestamp"

# Хранилище статуса последнего ретраина
retrain_status = {
    "last_retrain": None,
    "last_retrain_success": False,
    "total_retrains": 0,
    "status": "idle"  # idle, running, success, error
}

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
    "web.config", ".aws", ".azure", ".docker", "kubernetes", "terraform",
    "wp-json", "wp-login", "xmlrpc.php", "rest/api", "batch/v1",
    "wp-json/batch", "wp-json/wp/v2", "wp-json/oembed"
]

SUSPICIOUS_UA_PATTERNS = [
    "python-requests", "curl/", "wget/", "scrapy", "nikto", "nmap",
    "sqlmap", "masscan", "zgrab", "gobuster", "dirbuster", "wfuzz",
    "nuclei", "burp", "acunetix", "nessus", "openvas",
    "wordpress", "wp-cli", "jetpack"
]

# Хранилище rate limiting: IP -> список временных меток
rate_limit_store: Dict[str, List[float]] = defaultdict(list)
rate_limit_lock = threading.Lock()

# Хранилище атак: IP -> счётчик попыток
attack_store: Dict[str, int] = defaultdict(int)
attack_lock = threading.Lock()
MAX_ATTACK_ATTEMPTS = 5  # после N попыток - бан

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
    client_ip = request.client.host if request.client else "unknown"
    
    # Проверка User-Agent
    for suspicious in SUSPICIOUS_UA_PATTERNS:
        if suspicious in ua:
            return True, f"Подозрительный UA: {suspicious}"
    
    # Проверка путей
    for suspicious in SUSPICIOUS_PATHS:
        if suspicious in path:
            # Увеличиваем счётчик атак
            with attack_lock:
                attack_store[client_ip] += 1
                if attack_store[client_ip] >= MAX_ATTACK_ATTEMPTS:
                    # Бан IP
                    blocked_ips[client_ip] = datetime.now() + BLOCK_DURATION
                    logger.warning(f"🚫 IP забанен за многократные атаки: {client_ip} ({attack_store[client_ip]} попыток)")
                    return True, f"IP забанен за атаки ({attack_store[client_ip]} попыток)"
            return True, f"Подозрительный путь: {suspicious}"
    
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

# === Импорт Wuglarst App для mount по /wuglarst ===
WUGLARST_APP = None
try:
    from Wuglarst.server_autonomous import app as wuglarst_app  # type: ignore
    WUGLARST_APP = wuglarst_app
    logger.info("✅ Wuglarst app импортирован — будет доступен по /wuglarst")
except ImportError as e:
    logger.warning(f"⚠️ Wuglarst app не импортирован: {e}")
except Exception as e:
    logger.warning(f"⚠️ Wuglarst app не импортирован: {e}")
# === КОНЕЦ ИМПОРТА WUGLARST ===

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

# === Автономный запуск девочек (оркестратор) ===
AUTO_GIRLS_ENABLED = os.getenv("AUTO_GIRLS_ENABLED", "true").lower() in ("true", "1", "yes")
GIRLS_TO_RUN = [g.strip() for g in os.getenv("GIRLS_TO_RUN", "hanako,fuyuki,lucy,futaba,shiori,nobuka,akva,latislane,celesta,naoto,yu,ayiko").split(",") if g.strip()]

def start_girls_orchestrator():
    """Запуск оркестратора всех девочек в фоне."""
    if not AUTO_GIRLS_ENABLED:
        logger.info("🔮 Автозапуск девочек: ОТКЛЮЧЁН")
        return
    
    logger.info(f"🔮 Автозапуск девочек: ВКЛЮЧЕНО ({len(GIRLS_TO_RUN)} девочек)")
    logger.info(f"   Список: {', '.join(GIRLS_TO_RUN)}")
    
    try:
        # Небольшая задержка перед стартом (ждем полной загрузки сервера)
        time.sleep(15)
        
        import subprocess
        
        orchestrator_path = Path(__file__).parent / "orchestrator.py"
        if not orchestrator_path.exists():
            logger.warning("⚠️ orchestrator.py не найден — девочки не запущены")
            return
        
        cmd = [sys.executable, str(orchestrator_path)] + GIRLS_TO_RUN
        
        logger.info(f"🚀 Запуск оркестратора: {' '.join(cmd)}")
        
        # Запускаем в фоне
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        
        # Читаем вывод в реальном времени
        def read_output():
            if process.stdout:
                for line in process.stdout:
                    prefix = "[Orchestrator] "
                    sys.stdout.write(prefix + line)
                    sys.stdout.flush()
        
        reader_thread = threading.Thread(target=read_output, daemon=True)
        reader_thread.start()
        
        logger.info(f"✅ Оркестратор запущен (PID: {process.pid})")
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска оркестратора: {e}")

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
    
    # === АВТОЗАПУСК ДЕВОЧЕК ===
    logger.info("🔮 Запуск оркестратора девочек...")
    start_girls_orchestrator()
    # === КОНЕЦ АВТОЗАПУСКА ДЕВОЧЕК ===
    
    # === АВТО-ОБУЧЕНИЕ МОДЕЛИ (РАЗ В ДЕНЬ) ===
    if AUTO_RETRAIN_ENABLED:
        logger.info(f"🧠 Авто-обучение модели: ВКЛЮЧЕНО")
        logger.info(f"   ⏱️ Интервал: {AUTO_RETRAIN_INTERVAL // 3600} часа(ов)")
        logger.info(f"   📊 Загружаем статус последнего ретраина...")
        
        # Загружаем статус
        if os.path.exists(LAST_RETRAIN_FILE):
            try:
                with open(LAST_RETRAIN_FILE, "r") as f:
                    retrain_status.update(json.load(f))
                logger.info(f"   ✅ Статус загружен: последний ретраин {retrain_status['last_retrain']}")
            except:
                logger.info("   ℹ️ Новый статус (первый запуск)")
        
        async def start_auto_retrain():
            """Запускает авто-обучение модели раз в день"""
            import subprocess
            
            async def retrain_cycle():
                """Выполняет один цикл ретраина"""
                try:
                    logger.info("🧠 ЗАПУСК АВТО-ОБУЧЕНИЯ МОДЕЛИ...")
                    retrain_status["status"] = "running"
                    
                    # Запускаем retrain.py
                    result = subprocess.run(
                        [sys.executable, "retrain.py", "--generate", "0"],
                        capture_output=True,
                        text=True,
                        timeout=7200  # 2 часа таймаут
                    )
                    
                    if result.returncode == 0:
                        # Сохраняем статус
                        retrain_status.update({
                            "last_retrain": datetime.now().isoformat(),
                            "last_retrain_success": True,
                            "total_retrains": retrain_status.get("total_retrains", 0) + 1,
                            "status": "success"
                        })
                        with open(LAST_RETRAIN_FILE, "w") as f:
                            json.dump(retrain_status, f)
                        logger.info("✅ АВТО-ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
                    else:
                        retrain_status["status"] = "error"
                        logger.error(f"❌ Ошибка авто-обучения: {result.stderr[:500]}")
                        
                except subprocess.TimeoutExpired:
                    logger.error("❌ Таймаут авто-обучения (2 часа)")
                    retrain_status["status"] = "error"
                except Exception as e:
                    logger.error(f"❌ Ошибка авто-обучения: {e}")
                    retrain_status["status"] = "error"
            
            # Запускаем первый ретраин через 5 минут после старта
            await asyncio.sleep(300)
            await retrain_cycle()
            
            # Потом каждые AUTO_RETRAIN_INTERVAL секунд
            while True:
                await asyncio.sleep(AUTO_RETRAIN_INTERVAL)
                await retrain_cycle()
        
        # Запускаем фоновую задачу
        asyncio.create_task(start_auto_retrain())
    else:
        logger.info("🧠 Авто-обучение модели: ОТКЛЮЧЕНО")
    # === КОНЕЦ АВТО-ОБУЧЕНИЯ ===
    

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

# === МОНТИРОВАНИЕ WUGLARST ПО /wuglarst ===
if WUGLARST_APP:
    app.mount("/wuglarst", WUGLARST_APP)
    logger.info("✅ Wuglarst смонтирован по пути /wuglarst")
# === КОНЕЦ МОНТИРОВАНИЯ ===


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
        "girls_enabled": AUTO_GIRLS_ENABLED,
        "girls_count": len(GIRLS_TO_RUN),
        "timestamp": datetime.now().isoformat(),
        "blocked_ips": len(blocked_ips),
        "rate_limit_active": RATE_LIMIT_REQUESTS > 0
    }


# === Endpoint: размер модели ===
@app.get("/model/size")
async def get_model_size():
    """Возвращает размер модели, токенизатора и обучающих данных"""
    def format_size(size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / 1024 ** 2:.2f} MB"
        else:
            return f"{size_bytes / 1024 ** 3:.2f} GB"

    def get_file_size(path):
        if os.path.exists(path):
            return os.path.getsize(path)
        return None

    model_size = get_file_size("models/chat_model.pth")
    tokenizer_size = get_file_size("data/tokenizer.json")
    conv_size = get_file_size("data/conversations.json")
    train_size = get_file_size("data/training_pairs.jsonl")

    result = {
        "model": {
            "path": "models/chat_model.pth",
            "exists": model_size is not None,
            "size_bytes": model_size,
            "size_human": format_size(model_size) if model_size else "Не найдена"
        },
        "tokenizer": {
            "path": "data/tokenizer.json",
            "exists": tokenizer_size is not None,
            "size_bytes": tokenizer_size,
            "size_human": format_size(tokenizer_size) if tokenizer_size else "Не найден"
        },
        "training_data": {
            "conversations_json": {
                "path": "data/conversations.json",
                "exists": conv_size is not None,
                "size_bytes": conv_size,
                "size_human": format_size(conv_size) if conv_size else "Не найден"
            },
            "training_pairs_jsonl": {
                "path": "data/training_pairs.jsonl",
                "exists": train_size is not None,
                "size_bytes": train_size,
                "size_human": format_size(train_size) if train_size else "Не найден"
            }
        },
        "total_size_bytes": sum(s for s in [model_size, tokenizer_size, conv_size, train_size] if s is not None),
        "total_size_human": format_size(sum(s for s in [model_size, tokenizer_size, conv_size, train_size] if s is not None)),
        "timestamp": datetime.now().isoformat()
    }

    return result


# === Endpoint: ручное обучение модели ===
@app.post("/retrain")
async def manual_retrain():
    """Ручной запуск обучения модели (ретраин)"""
    if retrain_status["status"] == "running":
        raise HTTPException(status_code=409, detail="Обучение уже запущено")
    
    import subprocess
    
    retrain_status["status"] = "running"
    
    try:
        logger.info("🧠 РУЧНОЙ ЗАПУСК ОБУЧЕНИЯ МОДЕЛИ...")
        
        result = subprocess.run(
            [sys.executable, "retrain.py", "--generate", "0"],
            capture_output=True,
            text=True,
            timeout=7200  # 2 часа таймаут
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
            
            return {
                "status": "success",
                "message": "Обучение завершено успешно",
                "total_retrains": retrain_status["total_retrains"],
                "last_retrain": retrain_status["last_retrain"]
            }
        else:
            retrain_status["status"] = "error"
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка обучения: {result.stderr[:500]}"
            )
            
    except subprocess.TimeoutExpired:
        retrain_status["status"] = "error"
        raise HTTPException(status_code=504, detail="Таймаут обучения (2 часа)")
    except Exception as e:
        retrain_status["status"] = "error"
        raise HTTPException(status_code=500, detail=str(e))


# === Endpoint: статус обучения ===
@app.get("/retrain/status")
async def retrain_status_endpoint():
    """Показывает статус последнего обучения модели"""
    return {
        "status": retrain_status["status"],
        "last_retrain": retrain_status["last_retrain"],
        "last_retrain_success": retrain_status["last_retrain_success"],
        "total_retrains": retrain_status["total_retrains"],
        "auto_retrain_enabled": AUTO_RETRAIN_ENABLED,
        "interval_seconds": AUTO_RETRAIN_INTERVAL,
        "interval_human": f"{AUTO_RETRAIN_INTERVAL // 3600} часа(ов)"
    }


# === Endpoint: генерация изображений Айко ===
from fastapi.responses import FileResponse

# Глобальный генератор
ayiko_generator = None
shiori_scanner = None
ojidania_analyzer = None

@app.on_event("startup")
async def init_ayiko_generator():
    """Инициализация генератора изображений Айко"""
    global ayiko_generator, shiori_scanner, ojidania_analyzer
    try:
        from ayiko.image_generator import AyikoImageGenerator
        ayiko_generator = AyikoImageGenerator()
        logger.info("OK Gen image Ayiko initialized")
    except ImportError:
        logger.warning("WARNING Module ayiko.image_generator not found")
    except Exception as e:
        logger.error(f"ERROR Init gen: {e}")
    
    # Инициализация сканера Шиори
    try:
        from shiori.wordpress_scanner import WordPressScanner
        shiori_scanner = WordPressScanner()
        logger.info("OK Scanner Shiori initialized")
    except ImportError:
        logger.warning("WARNING Module shiori.wordpress_scanner not found")
    except Exception as e:
        logger.error(f"ERROR Init scanner: {e}")
    
    # Инициализация анализатора Ojidania
    try:
        from ayiko.ojidania_analyzer import OjidaniaAnalyzer
        ojidania_analyzer = OjidaniaAnalyzer()
        logger.info("OK Ojidania Analyzer initialized")
    except ImportError:
        logger.warning("WARNING Module ayiko.ojidania_analyzer not found")
    except Exception as e:
        logger.error(f"ERROR Init analyzer: {e}")


@app.post("/ayiko/generate")
async def ayiko_generate_image(request: Request):
    """
    Генерация изображения через Айко
    
    Body JSON:
    {
        "type": "pixel|technical|description",
        "style": "character|landscape|abstract|pattern",
        "palette": "retro|vintage|neon|pastel|monochrome",
        "size": 64,
        "technical_type": "circuit|gear|blueprint",
        "description": "текстовое описание"
    }
    """
    if ayiko_generator is None:
        raise HTTPException(status_code=503, detail="Генератор не инициализирован")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Неверный JSON")
    
    try:
        img_type = body.get("type", "pixel")
        
        if img_type == "pixel":
            img = ayiko_generator.generate_pixel_art(
                size=body.get("size", 64),
                style=body.get("style", "character"),
                palette=body.get("palette", "retro")
            )
        elif img_type == "technical":
            img = ayiko_generator.generate_technical_drawing(
                size=(512, 512),
                type=body.get("technical_type", "circuit")
            )
        elif img_type == "description":
            result = ayiko_generator.generate_from_description(
                body.get("description", "")
            )
            return {
                "status": "success",
                "message": "Изображение сгенерировано",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=f"Неизвестный тип: {img_type}")
        
        # Сохраняем и возвращаем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ayiko_{timestamp}.png"
        filepath = ayiko_generator.output_dir / filename
        img.save(filepath)
        
        return {
            "status": "success",
            "message": "Изображение сгенерировано",
            "filename": filename,
            "size": img.size,
            "format": "PNG"
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ayiko/stats")
async def ayiko_stats():
    """Статистика сгенерированных изображений"""
    if ayiko_generator is None:
        raise HTTPException(status_code=503, detail="Генератор не инициализирован")
    
    return ayiko_generator.get_stats()


@app.get("/ayiko/generate/{image_id}")
async def ayiko_get_image(image_id: str):
    """Получение сгенерированного изображения"""
    if ayiko_generator is None:
        raise HTTPException(status_code=503, detail="Генератор не инициализирован")
    
    filepath = ayiko_generator.output_dir / f"{image_id}.png"
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    return FileResponse(filepath, media_type="image/png")


# === Endpoint: сканирование запроса Шиори ===
@app.post("/shiori/scan")
async def shiori_scan_request(request: Request):
    """
    Сканирование запроса через Шиори
    
    Body JSON:
    {
        "ip": "192.168.1.100",
        "path": "/wp-json/batch/v1",
        "method": "POST",
        "user_agent": "Mozilla/5.0",
        "headers": {},
        "body": {}
    }
    """
    if shiori_scanner is None:
        raise HTTPException(status_code=503, detail="Сканер Шиори не инициализирован")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Неверный JSON")
    
    try:
        result = shiori_scanner.scan_request(body)
        
        if result["is_attack"]:
            logger.warning(f"SECURITY Attack detected: {result['attack_type']} from {body.get('ip')}")
            
            if result["action"] == "block_ip":
                ip = body.get("ip", "unknown")
                blocked_ips[ip] = datetime.now() + BLOCK_DURATION
                logger.warning(f"BAN IP blocked: {ip}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка сканирования: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/shiori/stats")
async def shiori_stats():
    """Статистика атак от Шиори"""
    if shiori_scanner is None:
        raise HTTPException(status_code=503, detail="Сканер Шиори не инициализирован")
    
    return shiori_scanner.get_stats()


@app.get("/shiori/report")
async def shiori_report():
    """Отчёт безопасности от Шиори"""
    if shiori_scanner is None:
        raise HTTPException(status_code=503, detail="Сканер Шиори не инициализирован")
    
    return shiori_scanner.generate_report()


@app.post("/shiori/unblock/{ip}")
async def shiori_unblock_ip(ip: str, request: Request):
    """Разблокировка IP через Шиори"""
    if shiori_scanner is None:
        raise HTTPException(status_code=503, detail="Сканер Шиори не инициализирован")
    
    token = request.headers.get("X-Retrain-Token")
    if token != RETRAIN_TOKEN:
        raise HTTPException(status_code=403, detail="Неверный токен")
    
    success = shiori_scanner.unblock_ip(ip)
    if success:
        logger.info(f"UNBLOCK IP unblocked by Shiori: {ip}")
        return {"status": "success", "message": f"IP {ip} unblocked"}
    else:
        raise HTTPException(status_code=404, detail="IP not found in blocked list")


# === Endpoint: анализ изображений Ojidania ===
@app.post("/ayiko/ojidania/analyze")
async def analyze_ojidania_image(request: Request):
    """
    Анализ изображения через Ojidania
    
    Body JSON:
    {
        "image_path": "ayiko/ojidania/photo.jpg"
    }
    """
    if ojidania_analyzer is None:
        raise HTTPException(status_code=503, detail="Анализатор Ojidania не инициализирован")
    
    try:
        body = await request.json()
        image_path = body.get("image_path", "")
        
        if not image_path:
            raise HTTPException(status_code=400, detail="Не указан путь к изображению")
        
        result = ojidania_analyzer.analyze_image(image_path)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        logger.info(f"ANALYZE Image analyzed: {result['filename']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR Analyze image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ayiko/ojidania/batch")
async def batch_analyze_ojidania(request: Request):
    """
    Пакетный анализ всех изображений в ojidania
    
    Body JSON (опционально):
    {
        "directory": "ayiko/ojidania"
    }
    """
    if ojidania_analyzer is None:
        raise HTTPException(status_code=503, detail="Анализатор Ojidania не инициализирован")
    
    try:
        body = await request.json() if await request.body() else {}
        directory = body.get("directory", "ayiko/ojidania")
        
        results = ojidania_analyzer.batch_analyze(directory)
        
        logger.info(f"ANALYZE Batch analyzed {len(results)} images")
        return {
            "status": "success",
            "count": len(results),
            "results": results,
            "stats": ojidania_analyzer.get_stats()
        }
        
    except Exception as e:
        logger.error(f"ERROR Batch analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ayiko/ojidania/stats")
async def ojidania_stats():
    """Статистика анализа Ojidania"""
    if ojidania_analyzer is None:
        raise HTTPException(status_code=503, detail="Анализатор Ojidania не инициализирован")
    
    return ojidania_analyzer.get_stats()


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
        "shiori_scanner": {
            "total_attacks": shiori_scanner.attack_stats["total_attacks"] if shiori_scanner else 0,
            "blocked_attacks": shiori_scanner.attack_stats["blocked_attacks"] if shiori_scanner else 0,
            "by_type": shiori_scanner.attack_stats["by_type"] if shiori_scanner else {},
            "by_severity": shiori_scanner.attack_stats["by_severity"] if shiori_scanner else {}
        },
        "attacks": {
            "total_blocked": sum(attack_store.values()),
            "active_attackers": {ip: count for ip, count in attack_store.items() if count > 0}
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
    with attack_lock:
        if ip in attack_store:
            del attack_store[ip]
    
    logger.info(f"🔓 IP разблокирован: {ip}")
    return {"status": "success", "message": f"IP {ip} разблокирован"}


# === Endpoint: сбросить счётчик атак ===
@app.post("/security/reset-attacks")
async def reset_attacks(request: Request):
    """Сбрасывает счётчик атак для всех IP."""
    token = request.headers.get("X-Retrain-Token")
    if token != RETRAIN_TOKEN:
        raise HTTPException(status_code=403, detail="Неверный токен")
    
    with attack_lock:
        attack_store.clear()
    
    logger.info("🔄 Счётчик атак сброшен")
    return {"status": "success", "message": "Счётчик атак сброшен"}

    if ip in blocked_ips:
        del blocked_ips[ip]
        logger.info(f"✅ IP {ip} разблокирован администратором")
        return {"status": "ok", "detail": f"IP {ip} разблокирован"}
    else:
        return {"status": "ok", "detail": f"IP {ip} не был заблокирован"}


# === Эндпоинт: /girls/status — статус оркестратора ===
@app.get("/girls")
async def girls_status():
    """Показывает статус оркестратора девочек."""
    return {
        "status": "ok",
        "enabled": AUTO_GIRLS_ENABLED,
        "girls": GIRLS_TO_RUN,
        "count": len(GIRLS_TO_RUN),
        "message": "Девочки запущены автоматически при старте сервера"
    }


# === Эндпоинт: /girls/restart — перезапуск девочек ===
@app.post("/girls/restart")
async def girls_restart(request: Request):
    """Перезапускает оркестратор девочек."""
    token = request.headers.get("X-Retrain-Token")
    if token != RETRAIN_TOKEN:
        raise HTTPException(status_code=403, detail="Неверный токен")
    
    if not AUTO_GIRLS_ENABLED:
        return {"status": "ok", "detail": "Автозапуск девочек отключён"}
    
    logger.info("🔄 Перезапуск оркестратора девочек...")
    start_girls_orchestrator()
    return {"status": "ok", "detail": f"Оркестратор перезапущен ({len(GIRLS_TO_RUN)} девочек)"}


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
        },
        "research_monitor": {
            "enabled": True,
            "description": "Мониторинг исследований учёных (Ханако-гравитация, Фуюки-электричество, Люси-двигатели, Футаба-саморазвитие, Шиори-безопасность, Нобука-улучшения, Латислейн-тело, Селеста-интимная жизнь, Аква-математика/физика, Юи-сознание). Все подключены к Scientists Network.",
            "scientists": ["hanako", "fuyuki", "lucy", "futaba", "shiori", "nobuka", "latislane", "celest", "akva", "yu"],
            "features": [
                "Запуск/остановка исследований",
                "Статус и метрики в реальном времени",
                "События (теории, вычисления, циклы, открытия)",
                "Логи исследований",
                "Результаты (теории, вычисления, статьи)",
                "История исследований",
                "Потоковая передача событий (SSE)"
            ],
            "endpoints": [
                "GET /research/status - Статус всех ядер",
                "POST /research/start/{scientist} - Запустить исследования",
                "POST /research/stop/{scientist} - Остановить исследования",
                "GET /research/{scientist}/summary - Полная сводка",
                "GET /research/{scientist}/status - Детальный статус",
                "GET /research/{scientist}/events - События",
                "GET /research/{scientist}/logs - Логи",
                "GET /research/{scientist}/theories - Теории",
                "GET /research/{scientist}/calculations - Вычисления",
                "GET /research/{scientist}/papers - Статьи",
                "GET /research/{scientist}/history - История",
                "GET /research/live/{scientist} - SSE поток событий",
                "GET /research/live/all - SSE поток всех ядер"
            ]
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


# === Интеграция Latislane (система изучения тела и проектирования) ===
LATISLANE_ENABLED = os.getenv("LATISLANE_ENABLED", "true").lower() in ("true", "1", "yes")
latislane_core = None
LATISLANE_LOCK = threading.Lock()

if LATISLANE_ENABLED:
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from latislane import LatislaneCore
        latislane_core = LatislaneCore(project_root=str(BASE_DIR), demo_mode=True)
        logger.info("🧬 Latislane инициализирован (изучение тела + проектирование)")
    except Exception as e:
        logger.warning(f"⚠️ Latislane не загружен: {e}")
# === КОНЕЦ ИНТЕГРАЦИИ LATISLANE ===

# === Интеграция Celesta (система изучения интимной жизни) ===
CELESTA_ENABLED = os.getenv("CELESTA_ENABLED", "true").lower() in ("true", "1", "yes")
celesta_core = None
CELESTA_LOCK = threading.Lock()

if CELESTA_ENABLED:
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from celesta import CelestaCore
        celesta_core = CelestaCore(project_root=str(BASE_DIR), demo_mode=True)
        logger.info("🌹 Celesta инициализирована (изучение интимной жизни)")
    except Exception as e:
        logger.warning(f"⚠️ Celesta не загружена: {e}")
# === КОНЕЦ ИНТЕГРАЦИИ CELESTA ===

# ========================
# Research Monitor — мониторинг исследований учёных (Ханако, Фуюки, Люси, Футаба, Шиори, Нобука, Латислейн, Селеста, Аква, Юи)
# ========================
RESEARCH_MONITOR_ENABLED = os.getenv("RESEARCH_MONITOR_ENABLED", "true").lower() in ("true", "1", "yes")
research_monitor = None
RESEARCH_MONITOR_LOCK = threading.Lock()

if RESEARCH_MONITOR_ENABLED:
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from scientists_network.research_monitor import ResearchMonitor
        research_monitor = ResearchMonitor()
        research_monitor.initialize()
        logger.info("🔬 ResearchMonitor инициализирован (Ханако, Фуюки, Люси, Футаба, Шиори, Нобука, Латислейн, Селеста, Аква, Юи)")
    except Exception as e:
        logger.warning(f"⚠️ ResearchMonitor не загружен: {e}")
# === КОНЕЦ ИНТЕГРАЦИИ RESEARCH MONITOR ===


# ========================
# Latislane Endpoints (Система изучения тела и проектирования)
# ========================

# === Эндпоинт: /latislane/status — статус системы ===
@app.get("/latislane/status")
async def latislane_status():
    """Статус системы Латислейн."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        return {"status": "not available", "detail": "Latislane не загружен"}
    
    try:
        status = local_latislane.get_system_status()
        return {"status": "ok", "latislane": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/anatomy — отчёт по анатомии ===
@app.get("/latislane/anatomy")
async def latislane_anatomy():
    """Отчёт по изученной анатомии."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        return {"status": "not available", "detail": "Latislane не загружен"}
    
    try:
        report = local_latislane.get_anatomy_report()
        return {"status": "ok", "anatomy": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/study — запуск цикла обучения ===
@app.post("/latislane/study")
async def latislane_study(request: Request):
    """Запустить цикл обучения."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        body = await request.json() if request.method == "POST" else {}
        topics = body.get("topics")  # Список тем (опционально)
        batch_size = body.get("batch_size", 3)
        
        # Запуск в фоне
        async def _run_study():
            await local_latislane.run_study_cycle(topics=topics, batch_size=batch_size)
        
        asyncio.create_task(_run_study())
        
        return {"status": "ok", "message": "Цикл обучения запущен в фоне"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/design/mechanical — проектирование механического тела ===
@app.post("/latislane/design/mechanical")
async def latislane_design_mechanical(request: Request):
    """Спроектировать механическое тело."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        body = await request.json() if request.method == "POST" else {}
        name = body.get("name", f"Mechanical-{int(time.time())}")
        
        spec = local_latislane.design_mechanical_body(name=name)
        return {"status": "ok", "body": spec.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/design/bionic — проектирование бионического тела ===
@app.post("/latislane/design/bionic")
async def latislane_design_bionic(request: Request):
    """Спроектировать бионическое тело."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        body = await request.json() if request.method == "POST" else {}
        name = body.get("name", f"Bionic-{int(time.time())}")
        
        spec = local_latislane.design_bionic_body(name=name)
        return {"status": "ok", "body": spec.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/design/organic — проектирование органического тела ===
@app.post("/latislane/design/organic")
async def latislane_design_organic(request: Request):
    """Спроектировать органическое тело."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        body = await request.json() if request.method == "POST" else {}
        name = body.get("name", f"Organic-{int(time.time())}")
        
        spec = local_latislane.design_organic_body(name=name)
        return {"status": "ok", "body": spec.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/chat — чат с Латислейн ===
@app.post("/latislane/chat")
async def latislane_chat(request: Request):
    """Чат с системой Латислейн."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        body = await request.json()
        message = body.get("message", "")
        
        response = local_latislane.chat_response(message)
        return {"status": "ok", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/learn — начать изучение анатомии ===
@app.post("/latislane/learn")
async def latislane_learn():
    """Начать изучение анатомии."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        local_latislane.start_anatomy_study()
        return {"status": "ok", "message": "Изучение анатомии начато"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/evolution — статус эволюции ===
@app.get("/latislane/evolution")
async def latislane_evolution():
    """Статус эволюции Латислейн."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        return {"status": "not available", "detail": "Latislane не загружен"}
    
    try:
        report = local_latislane.evolution.get_evolution_report()
        return {"status": "ok", "evolution": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/evolve — перейти к следующему этапу ===
@app.post("/latislane/evolve")
async def latislane_evolve():
    """Принудительно перейти к следующему этапу эволюции."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        # Проверка возможности перехода
        learned_topics = len(local_latislane.learning_engine.topic_progress)
        
        if local_latislane.evolution.can_advance(learned_topics):
            local_latislane.evolution.advance(reason="api_request")
            return {
                "status": "ok",
                "message": f"Эволюция: {local_latislane.evolution.current_stage.value}",
                "evolution": local_latislane.evolution.get_current_stage_info()
            }
        else:
            return {
                "status": "not_ready",
                "message": "Ещё рано переходить к следующему этапу",
                "current_stage": local_latislane.evolution.get_current_stage_info()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/autonomous — запуск автономного обучения ===
@app.post("/latislane/autonomous")
async def latislane_autonomous(request: Request):
    """Запустить автономное обучение."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        body = await request.json() if request.method == "POST" else {}
        interval = body.get("interval_minutes", 10)
        
        local_latislane.start_autonomous_learning(interval_minutes=interval)
        return {"status": "ok", "message": f"Автономное обучение запущено (интервал: {interval} мин)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/self-improve — саморазвитие ===
@app.post("/latislane/self-improve")
async def latislane_self_improve():
    """Запустить саморазвитие."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        async def _run_improve():
            await local_latislane.self_improve()
        
        asyncio.create_task(_run_improve())
        return {"status": "ok", "message": "Саморазвитие запущено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/character — характер ===
@app.get("/latislane/character")
async def latislane_character():
    """Получить информацию о характере Латислейн."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        report = local_latislane.character.generate_character_report()
        return {"status": "ok", "character": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/character/reinforce — укрепить черту ===
@app.post("/latislane/character/reinforce")
async def latislane_character_reinforce(request: Request):
    """Укрепить черту характера."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        body = await request.json()
        trait_id = body.get("trait_id", "")
        amount = body.get("amount", 0.1)
        context = body.get("context", "")
        
        local_latislane.character.reinforce_trait(trait_id, amount, context)
        return {"status": "ok", "message": f"Черта '{trait_id}' укреплена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/social — социальные взаимодействия ===
@app.get("/latislane/social")
async def latislane_social():
    """Получить информацию о социальных взаимодействиях."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        report = local_latislane.social.get_social_report()
        return {"status": "ok", "social": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/social/interact — взаимодействие с сёстрой ===
@app.post("/latislane/social/interact")
async def latislane_social_interact(request: Request):
    """Взаимодействовать с сёстрой."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        body = await request.json()
        sister = body.get("sister", "")
        interaction_type = body.get("type", "обучение")
        quality = body.get("quality", 0.7)
        context = body.get("context", "")
        
        result = local_latislane.social.interact_with_sister(sister, interaction_type, quality, context)
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/reports — отчёты ===
@app.get("/latislane/reports")
async def latislane_reports():
    """Получить отчёты и уровни знаний."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        level_overview = local_latislane.reports.get_level_overview()
        recent = local_latislane.reports.get_recent_reports(10)
        return {"status": "ok", "levels": level_overview, "recent": recent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/reports/daily — ежедневный отчёт ===
@app.post("/latislane/reports/daily")
async def latislane_reports_daily():
    """Создать ежедневный отчёт."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        report = local_latislane.reports.create_daily_report()
        if report:
            return {"status": "ok", "message": f"Отчёт создан: {report.title}"}
        else:
            return {"status": "ok", "message": "Отчёт уже написан сегодня"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/full-report — полный отчёт ===
@app.get("/latislane/full-report")
async def latislane_full_report():
    """Сгенерировать полный отчёт."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        report_text = local_latislane.reports.generate_full_report()
        return {"status": "ok", "report": report_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /latislane/autonomous/stop — остановить автономную работу ===
@app.post("/latislane/autonomous/stop")
async def latislane_autonomous_stop():
    """Остановить автономное обучение."""
    local_latislane = None
    with LATISLANE_LOCK:
        local_latislane = latislane_core
    
    if local_latislane is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    
    try:
        local_latislane.stop_autonomous_learning()
        return {"status": "ok", "message": "Автономное обучение остановлено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Celesta Endpoints (Система изучения интимной жизни)
# ========================

# === Эндпоинт: /celesta/status — статус системы ===
@app.get("/celesta/status")
async def celesta_status():
    """Статус системы Селеста."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        return {"status": "not available", "detail": "Celesta не загружена"}
    
    try:
        status = local_celesta.get_system_status()
        return {"status": "ok", "celesta": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/intimacy — отчёт по интимным знаниям ===
@app.get("/celesta/intimacy")
async def celesta_intimacy():
    """Отчёт по изученной интимной жизни."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        return {"status": "not available", "detail": "Celesta не загружена"}
    
    try:
        report = local_celesta.get_intimacy_report()
        return {"status": "ok", "intimacy": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/stage/{stage} — детали этапа ===
@app.get("/celesta/stage/{stage}")
async def celesta_stage(stage: str):
    """Детали конкретного этапа интимной жизни."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    
    try:
        from celesta.intimacy_modules import IntimacyStage
        intimacy_stage = IntimacyStage(stage)
        details = local_celesta.get_stage_details(intimacy_stage)
        return {"status": "ok", "stage": details}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Неизвестный этап: {stage}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/consequences — последствия ===
@app.post("/celesta/consequences")
async def celesta_consequences(request: Request):
    """Получить информацию о последствиях."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    
    try:
        body = await request.json()
        scenario = body.get("scenario", "normal")  # "excessive", "interrupted", "normal"
        
        info = local_celesta.get_consequences_info(scenario)
        return {"status": "ok", "consequences": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/race/{race} — особенности расы ===
@app.get("/celesta/race/{race}")
async def celesta_race(race: str):
    """Получить информацию об особенностях расы."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    
    try:
        info = local_celesta.get_race_specific_info(race)
        return {"status": "ok", "race": race, "info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/study — запуск цикла обучения ===
@app.post("/celesta/study")
async def celesta_study(request: Request):
    """Запустить цикл обучения."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    
    try:
        body = await request.json() if request.method == "POST" else {}
        topics = body.get("topics")
        batch_size = body.get("batch_size", 3)
        
        async def _run_study():
            await local_celesta.run_study_cycle(topics=topics, batch_size=batch_size)
        
        asyncio.create_task(_run_study())
        
        return {"status": "ok", "message": "Цикл обучения запущен в фоне"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/chat — чат с Селестой ===
@app.post("/celesta/chat")
async def celesta_chat(request: Request):
    """Чат с системой Селеста."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    
    try:
        body = await request.json()
        message = body.get("message", "")
        
        response = local_celesta.chat_response(message)
        return {"status": "ok", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/learn — начать изучение ===
@app.post("/celesta/learn")
async def celesta_learn():
    """Начать изучение интимной жизни."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    
    try:
        local_celesta.start_intimacy_study()
        return {"status": "ok", "message": "Изучение интимной жизни начато"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/autonomous — запуск автономного обучения ===
@app.post("/celesta/autonomous")
async def celesta_autonomous(request: Request):
    """Запустить автономное обучение."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    
    try:
        body = await request.json() if request.method == "POST" else {}
        interval = body.get("interval_minutes", 10)
        
        local_celesta.start_autonomous_learning(interval_minutes=interval)
        return {"status": "ok", "message": f"Автономное обучение запущено (интервал: {interval} мин)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /celesta/self-improve — саморазвитие ===
@app.post("/celesta/self-improve")
async def celesta_self_improve():
    """Запустить саморазвитие."""
    local_celesta = None
    with CELESTA_LOCK:
        local_celesta = celesta_core
    
    if local_celesta is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    
    try:
        async def _run_improve():
            await local_celesta.self_improve()
        
        asyncio.create_task(_run_improve())
        return {"status": "ok", "message": "Саморазвитие запущено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========================
# Research Monitor Endpoints — мониторинг исследований учёных
# ========================

# === Эндпоинт: /research/status — статус всех ядер ===
@app.get("/research/status")
async def research_status():
    """Статус всех ядер учёных (Ханако, Фуюки, Люси, Футаба, Шиори, Нобука, Латислейн, Селеста, Аква, Юи)."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            return {"status": "not available", "detail": "ResearchMonitor не загружен"}
        
        assert research_monitor is not None
        
        try:
            status = research_monitor.get_all_status()
            return {"status": "ok", "research": status}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /research/start — запуск исследований ядра ===
@app.post("/research/start/{scientist}")
async def research_start(scientist: str):
    """Запустить исследования указанного ядра (hanako/fuyuki/lucy/futaba/shiori/nobuka/latislane/celest/akva)."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        result = research_monitor.start_research(scientist)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["detail"])
        
        return result


# === Эндпоинт: /research/stop — остановка исследований ядра ===
@app.post("/research/stop/{scientist}")
async def research_stop(scientist: str):
    """Остановить исследования указанного ядра (hanako/fuyuki/lucy/futaba/shiori/nobuka/latislane/celest/akva)."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        result = research_monitor.stop_research(scientist)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["detail"])
        
        return result


# === Эндпоинт: /research/{scientist}/summary — полная сводка по ядру ===
@app.get("/research/{scientist}/summary")
async def research_summary(scientist: str):
    """Получить полную сводку по исследованиям ядра."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        summary = research_monitor.get_research_summary(scientist)
        
        if summary is None:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        return {"status": "ok", "scientist": scientist, "summary": summary}


# === Эндпоинт: /research/{scientist}/events — события ядра ===
@app.get("/research/{scientist}/events")
async def research_events(scientist: str, limit: int = 50, event_type: Optional[str] = None):
    """Получить события ядра (теории, вычисления, циклы и т.д.)."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        events = core.get_all_events(limit=limit, event_type=event_type)
        live_events = core.get_events(limit=10)
        
        return {
            "status": "ok",
            "scientist": scientist,
            "events": events,
            "live_events": live_events,
            "total_events": len(events),
        }


# === Эндпоинт: /research/{scientist}/data — данные Юи (сознание, перенос) ===
@app.get("/research/{scientist}/data")
async def research_data(scientist: str):
    """Получить специализированные данные ядра."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        if scientist.lower() == 'yu':
            consciousness_models = core.get_consciousness_models(limit=20)
            embodiments = core.get_embodiments(limit=20)
            transfer_records = core.get_transfer_records(limit=20)
            
            return {
                "status": "ok",
                "scientist": scientist,
                "consciousness_models": consciousness_models,
                "embodiments": embodiments,
                "transfer_records": transfer_records,
                "count": {
                    "models": len(consciousness_models),
                    "embodiments": len(embodiments),
                    "transfers": len(transfer_records),
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Этот эндпоинт только для Юи")


# === Эндпоинт: /research/{scientist}/logs — логи ядра ===
@app.get("/research/{scientist}/logs")
async def research_logs(scientist: str, limit: int = 100):
    """Получить последние логи ядра."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        logs = core.get_logs(limit=limit)
        
        return {
            "status": "ok",
            "scientist": scientist,
            "logs": logs,
            "count": len(logs),
        }


# === Эндпоинт: /research/{scientist}/theories — теории ядра ===
@app.get("/research/{scientist}/theories")
async def research_theories(scientist: str, limit: int = 20):
    """Получить теории, построенные ядром."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        theories = core.get_theories(limit=limit)
        
        return {
            "status": "ok",
            "scientist": scientist,
            "theories": theories,
            "count": len(theories),
        }


# === Эндпоинт: /research/{scientist}/calculations — вычисления ядра ===
@app.get("/research/{scientist}/calculations")
async def research_calculations(scientist: str, limit: int = 20):
    """Получить вычисления, выполненные ядром."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        calculations = core.get_calculations(limit=limit)
        
        return {
            "status": "ok",
            "scientist": scientist,
            "calculations": calculations,
            "count": len(calculations),
        }


# === Эндпоинт: /research/{scientist}/papers — статьи ядра ===
@app.get("/research/{scientist}/papers")
async def research_papers(scientist: str, limit: int = 20):
    """Получить статьи, изученные ядром."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        papers = core.get_papers(limit=limit)
        
        return {
            "status": "ok",
            "scientist": scientist,
            "papers": papers,
            "count": len(papers),
        }


# === Эндпоинт: /research/{scientist}/history — история исследований ===
@app.get("/research/{scientist}/history")
async def research_history(scientist: str, limit: int = 50):
    """Получить историю исследований ядра."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        history = core.get_research_history(limit=limit)
        
        return {
            "status": "ok",
            "scientist": scientist,
            "history": history,
            "count": len(history),
        }


# === Эндпоинт: /research/{scientist}/status — детальное состояние ядра ===
@app.get("/research/{scientist}/status")
async def research_core_status(scientist: str):
    """Получить детальное состояние ядра."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        return {
            "status": "ok",
            "scientist": scientist,
            "core": core.get_status(),
        }


# === Эндпоинт: /research/live — поток событий в реальном времени (SSE) ===
@app.get("/research/live/{scientist}")
async def research_live(scientist: str):
    """
    Stream событий ядра в реальном времени (Server-Sent Events).
    
    Поддерживаемые типы событий:
    - STARTED / STOPPED — запуск/остановка
    - CYCLE — начало цикла исследований
    - THEORY — построение новой теории
    - CALCULATION — выполнение вычисления
    - PAPERS — обнаружение новых статей
    - DISCOVERY — находка (секреты молний/гравитации)
    - ERROR — ошибка
    """
    from fastapi.responses import StreamingResponse
    
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        core = research_monitor.get_core(scientist)
        if not core:
            raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
        
        def event_stream():
            """Генератор событий для SSE."""
            assert core is not None
            while True:
                try:
                    # Получаем новые события из очереди
                    events = core.get_events(limit=10)
                    
                    for event in events:
                        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                    
                    # Проверяем статус ядра
                    status = core.get_status()
                    status_event = {
                        "type": "status",
                        "scientist": scientist,
                        "data": status,
                    }
                    yield f"data: {json.dumps(status_event, ensure_ascii=False)}\n\n"
                    
                    time.sleep(2)  # Интервал обновления
                
                except GeneratorExit:
                    break
                except Exception as e:
                    error_event = {
                        "type": "error",
                        "scientist": scientist,
                        "data": {"error": str(e)},
                    }
                    yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
                    time.sleep(5)
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Отключаем буферизацию Nginx
            }
        )


# === Эндпоинт: /research/live/all — поток событий всех ядер ===
@app.get("/research/live/all")
async def research_live_all():
    """
    Поток событий всех ядер учёных в реальном времени (SSE).
    """
    from fastapi.responses import StreamingResponse
    
    if research_monitor is None:
        raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
    
    assert research_monitor is not None
    
    with RESEARCH_MONITOR_LOCK:
        assert research_monitor is not None
        
        def event_stream():
            """Генератор событий для SSE."""
            assert research_monitor is not None
            while True:
                try:
                    for name, core in research_monitor.cores.items():
                        events = core.get_events(limit=5)
                        
                        for event in events:
                            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                    
                    # Общий статус
                    status = research_monitor.get_all_status()
                    status_event = {
                        "type": "status",
                        "data": status,
                    }
                    yield f"data: {json.dumps(status_event, ensure_ascii=False)}\n\n"
                    
                    time.sleep(2)
                
                except GeneratorExit:
                    break
                except Exception as e:
                    error_event = {
                        "type": "error",
                        "data": {"error": str(e)},
                    }
                    yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
                    time.sleep(5)
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )


# ========================
# Scientists Network API — коммуникация между учёными
# ========================

# === Эндпоинт: /network/status — статус сети ===
@app.get("/network/status")
async def network_status():
    """Статус Scientists Network и коммуникации."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            return {"status": "not available", "detail": "ResearchMonitor не загружен"}
        
        assert research_monitor is not None
        
        try:
            stats = research_monitor.network.get_stats()
            return {"status": "ok", "network": stats}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /network/history — история сообщений ===
@app.get("/network/history")
async def network_history(limit: int = 50, sender: Optional[str] = None):
    """Получить историю сообщений между учёными."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        
        try:
            messages = research_monitor.network.get_message_history(
                limit=limit,
                sender=sender,
            )
            return {
                "status": "ok",
                "messages": messages,
                "count": len(messages),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# === Эндпоинт: /network/send — отправить сообщение ===
@app.post("/network/send")
async def network_send(
    sender: str,
    recipient: str,
    content: str,
    message_type: str = "message",
    priority: str = "normal",
):
    """Отправить сообщение от одного учёного другому."""
    with RESEARCH_MONITOR_LOCK:
        if research_monitor is None:
            raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
        
        assert research_monitor is not None
        
        try:
            from scientists_network.network import Message, MessageType, RequestPriority
            
            msg_type = MessageType(message_type)
            msg_priority = RequestPriority(priority)
            
            message = Message(
                message_type=msg_type,
                sender=sender,
                recipient=recipient,
                content=content,
                priority=msg_priority,
            )
            
            success = research_monitor.network.send_message(message)
            
            if success:
                return {
                    "status": "ok",
                    "message": "Сообщение отправлено",
                    "sender": sender,
                    "recipient": recipient,
                }
            else:
                raise HTTPException(status_code=400, detail="Не удалось отправить сообщение")
        
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Ошибка типа сообщения: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


# ========================
# === Запуск (для uvicorn) ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info("📌 Сервер готов. Запускаем...")
    uvicorn.run("main:app", host="0.0.0.0", port=port)