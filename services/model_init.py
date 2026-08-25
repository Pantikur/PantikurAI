# services/model_init.py — Инициализация модели и WebSearch

import asyncio
import logging
from pathlib import Path

from config import BASE_DIR
from services.model_loader import load_qwen_model

logger = logging.getLogger("model_init")

_qwen_cache_ref: list = [None]
_web_search_ref: list = [None]
_chatbot_lock = None


def init_chatbot_lock():
    """Возвращает RLock для потокобезопасного доступа к модели."""
    global _chatbot_lock
    if _chatbot_lock is None:
        import threading

        _chatbot_lock = threading.RLock()
    return _chatbot_lock


def get_chatbot_ref():
    """Возвращает ссылку на загруженную модель."""
    return _qwen_cache_ref


def get_web_search_ref():
    """Возвращает ссылку на WebSearch."""
    return _web_search_ref


def get_chatbot_lock():
    return _chatbot_lock


async def load_chatbot():
    """Асинхронно загружает Qwen2.5-3B."""
    logger.info("🔁 Загружаю Qwen2.5-3B (в фоне)...")
    qwen_model = await asyncio.to_thread(load_qwen_model)
    if qwen_model is None:
        logger.warning("⚠️ Модель не загружена")
        return None

    _qwen_cache_ref[0] = qwen_model  # type: ignore[index]
    logger.info("✅ Qwen2.5-3B успешно загружен!")
    return qwen_model


async def init_web_search():
    """Асинхронно инициализирует WebSearch (Selenium)."""
    try:
        from Wuglarst.src.web_search import WebSearch

        def _init():
            ws = WebSearch()
            ws.init_driver()
            return ws

        ws_result = await asyncio.to_thread(_init)
        if ws_result is not None and ws_result.driver is not None:
            _web_search_ref[0] = ws_result  # type: ignore[index]
            logger.info("✅ WebSearch инициализирован")
            return ws_result
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации WebSearch: {e}")

    return None


async def reload_model():
    """Перезагружает модель (вызывается при сигнале от Наото)."""
    signal_file = BASE_DIR / "data" / ".model_needs_reload"
    if not signal_file.exists():
        return

    logger.info("📡 Сигнал от Наото: перезагрузка модели...")
    try:
        _qwen_cache_ref[0] = None
        qwen_model = load_qwen_model()
        lock = init_chatbot_lock()
        with lock:
            _qwen_cache_ref[0] = qwen_model  # type: ignore[index]
        logger.info("✅ Модель перезагружена!")
        signal_file.unlink()
    except Exception as e:
        logger.error(f"❌ Перезагрузка не удалась: {e}")
