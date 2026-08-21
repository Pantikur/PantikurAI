# config.py — Конфигурация и константы для Pantikur ChatBot API

import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent

# === Пути ===
LOCAL_MODEL_PATH = str(BASE_DIR / "models" / "qwen2.5-3b")
DATA_PATH = BASE_DIR / "data" / "tokenizer.json"
CONVERSATIONS_JSON = BASE_DIR / "data" / "conversations.json"

# Wuglarst
WUGLARST_DIR = BASE_DIR / "Wuglarst"
WUGLARST_SRC_DIR = WUGLARST_DIR / "src"

# === Автономное обучение из книг ===
AUTO_BOOK_LEARNING_ENABLED = os.getenv("AUTO_BOOK_LEARNING", "true").lower() in ("true", "1", "yes")
AUTO_BOOK_LEARNING_CYCLE = int(os.getenv("AUTO_BOOK_LEARNING_CYCLE", "10"))
AUTO_BOOK_MAX_BOOKS = int(os.getenv("AUTO_BOOK_MAX_BOOKS", "5"))

# === Авто-обучение модели ===
AUTO_RETRAIN_ENABLED = os.getenv("AUTO_RETRAIN", "true").lower() in ("true", "1", "yes")
AUTO_RETRAIN_INTERVAL = int(os.getenv("AUTO_RETRAIN_INTERVAL", "86400"))
LAST_RETRAIN_FILE = "data/.last_retrain_timestamp"

retrain_status = {
    "last_retrain": None,
    "last_retrain_success": False,
    "total_retrains": 0,
    "status": "idle"
}

# === Rate Limiting ===
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
RATE_LIMIT_WINDOW = 60

# === Безопасность ===
SUSPICIOUS_UA_PATTERNS = [
    "python-requests", "curl/", "wget/", "scrapy", "nikto", "nmap",
    "sqlmap", "masscan", "zgrab", "gobuster", "dirbuster", "wfuzz",
    "nuclei", "burp", "acunetix", "nessus", "openvas",
    "wordpress", "wp-cli", "jetpack"
]

SUSPICIOUS_PATHS = [
    ".env", ".git", ".svn", ".hg", "wp-admin", "wp-content", "phpinfo",
    "phpmyadmin", "adminer", "shell", "cmd", "exec", "eval", "backup",
    ".sql", ".dump", ".pem", ".key", ".htaccess", ".htpasswd", "config.php",
    "web.config", ".aws", ".azure", ".docker", "kubernetes", "terraform",
    "wp-json", "wp-login", "xmlrpc.php", "rest/api", "batch/v1",
    "wp-json/batch", "wp-json/wp/v2", "wp-json/oembed"
]

# === Хранилища безопасности ===
WHITELISTED_IPS_RAW = os.getenv("WHITELISTED_IPS", "127.0.0.1,::1,172.18.0.2")
WHITELISTED_IPS = set(ip.strip() for ip in WHITELISTED_IPS_RAW.split(","))

MAX_ATTACK_ATTEMPTS = 5
BLOCK_DURATION = timedelta(hours=24)

# === Автопоиск слов ===
AUTO_WEB_SEARCH_ENABLED = os.getenv("AUTO_WEB_SEARCH", "true").lower() in ("true", "1", "yes")
AUTO_WEB_SEARCH_INTERVAL = int(os.getenv("AUTO_WEB_SEARCH_INTERVAL", "3600"))
AUTO_WEB_SEARCH_BATCH_SIZE = int(os.getenv("AUTO_WEB_SEARCH_BATCH_SIZE", "10"))
AUTO_WEB_SEARCH_MIN_LENGTH = int(os.getenv("AUTO_WEB_SEARCH_MIN_LENGTH", "2"))
AUTO_WEB_SEARCH_EXTRACT_DEPTH = int(os.getenv("AUTO_WEB_SEARCH_EXTRACT_DEPTH", "1"))
AUTO_WEB_SEARCH_MAX_NEW_WORDS = int(os.getenv("AUTO_WEB_SEARCH_MAX_NEW_WORDS", "10"))

# === Оркестратор девочек ===
AUTO_GIRLS_ENABLED = os.getenv("AUTO_GIRLS_ENABLED", "true").lower() in ("true", "1", "yes")
GIRLS_TO_RUN = [g.strip() for g in os.getenv("GIRLS_TO_RUN", "hanako,fuyuki,lucy,futaba,shiori,nobuka,akva,latislane,celesta,naoto,yu,ayiko").split(",") if g.strip()]

# === Логирование ===
APP_LOG_FILE = os.getenv("APP_LOG_FILE", "logs/app.log")

# === Токены ===
GIGACHAT_TOKEN = os.getenv("GIGACHAT_TOKEN")
RETRAIN_TOKEN = os.getenv("RETRAIN_TOKEN")

# === Флаги интеграций ===
LATISLANE_ENABLED = os.getenv("LATISLANE_ENABLED", "true").lower() in ("true", "1", "yes")
CELESTA_ENABLED = os.getenv("CELESTA_ENABLED", "true").lower() in ("true", "1", "yes")
RESEARCH_MONITOR_ENABLED = os.getenv("RESEARCH_MONITOR_ENABLED", "true").lower() in ("true", "1", "yes")
