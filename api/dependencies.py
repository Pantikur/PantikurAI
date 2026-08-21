# api/dependencies.py — Зависимости для FastAPI Dependency Injection

def get_chatbot_ref():
    from main import chatbot_ref
    return chatbot_ref

def get_CHATBOT_LOCK():
    from main import CHATBOT_LOCK
    return CHATBOT_LOCK

def get_LATISLANE_LOCK():
    from main import LATISLANE_LOCK
    return LATISLANE_LOCK

def get_CELESTA_LOCK():
    from main import CELESTA_LOCK
    return CELESTA_LOCK

def get_RESEARCH_MONITOR_LOCK():
    from main import RESEARCH_MONITOR_LOCK
    return RESEARCH_MONITOR_LOCK

def get_latislane_core():
    from main import latislane_core
    return latislane_core

def get_celesta_core():
    from main import celesta_core
    return celesta_core

def get_research_monitor():
    from main import research_monitor
    return research_monitor


# === Зависимости для значений конфигурации ===

from config import BASE_DIR, RETRAIN_TOKEN, GIGACHAT_TOKEN


def get_base_dir():
    """Возвращает BASE_DIR из конфига."""
    return BASE_DIR


def get_retrain_token():
    """Возвращает RETRAIN_TOKEN из конфига."""
    return RETRAIN_TOKEN


def get_gigachat_token():
    """Возвращает GIGACHAT_TOKEN из конфига."""
    return GIGACHAT_TOKEN
