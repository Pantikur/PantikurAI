# api/dependencies.py — Зависимости для FastAPI Dependency Injection

from services.model_init import get_chatbot_ref, get_chatbot_lock
from services.service_init import (
    get_latislane_lock, get_celesta_lock, get_research_monitor_lock,
    get_latislane, get_celesta, get_research_monitor,
)


def get_chatbot_ref_dep():
    """Зависимость для получения chatbot_ref."""
    return get_chatbot_ref()


def get_CHATBOT_LOCK():
    """Зависимость для получения CHATBOT_LOCK."""
    return get_chatbot_lock()


def get_LATISLANE_LOCK():
    """Зависимость для получения LATISLANE_LOCK."""
    return get_latislane_lock()


def get_CELESTA_LOCK():
    """Зависимость для получения CELESTA_LOCK."""
    return get_celesta_lock()


def get_RESEARCH_MONITOR_LOCK():
    """Зависимость для получения RESEARCH_MONITOR_LOCK."""
    return get_research_monitor_lock()


def get_latislane_core():
    """Зависимость для получения LatislaneCore."""
    return get_latislane()


def get_celesta_core():
    """Зависимость для получения CelestaCore."""
    return get_celesta()


def get_research_monitor_dep():
    """Зависимость для получения ResearchMonitor."""
    return get_research_monitor()


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
