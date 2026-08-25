# services/background_tasks.py — Фоновые задачи (автообучение, автопоиск, ретраин)

import asyncio
import logging
import sys
from pathlib import Path

from config import (
    AUTO_BOOK_LEARNING_ENABLED, AUTO_BOOK_LEARNING_CYCLE, AUTO_BOOK_MAX_BOOKS,
    AUTO_RETRAIN_ENABLED, AUTO_RETRAIN_INTERVAL, LAST_RETRAIN_FILE, retrain_status,
    AUTO_WEB_SEARCH_ENABLED, AUTO_WEB_SEARCH_INTERVAL, AUTO_WEB_SEARCH_BATCH_SIZE,
    AUTO_WEB_SEARCH_MIN_LENGTH, AUTO_WEB_SEARCH_EXTRACT_DEPTH, AUTO_WEB_SEARCH_MAX_NEW_WORDS,
    RETRAIN_TOKEN,
)

logger = logging.getLogger("background_tasks")


async def start_auto_book_learning():
    """Запускает автообучение из книг."""
    if not AUTO_BOOK_LEARNING_ENABLED:
        return

    logger.info("📚 Автообучение из книг: ВКЛЮЧЕНО")

    async def _run():
        await asyncio.sleep(10)
        try:
            from utils.auto_book_learning import AutoBookLearning
            controller = AutoBookLearning(
                cycle_minutes=AUTO_BOOK_LEARNING_CYCLE,
                max_books_per_cycle=AUTO_BOOK_MAX_BOOKS,
                topics_per_cycle=2,
            )

            # Запускаем в отдельном потоке без get_event_loop()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, controller.run_continuous)
        except Exception as e:
            logger.error(f"❌ Ошибка автообучения из книг: {e}")

    asyncio.create_task(_run())


async def start_auto_retrain():
    """Запускает авто-обучение модели."""
    if not AUTO_RETRAIN_ENABLED:
        return

    logger.info("🧠 Авто-обучение модели: ВКЛЮЧЕНО")

    async def retrain_cycle():
        try:
            import subprocess as sp
            retrain_status["status"] = "running"
            result = sp.run(
                [sys.executable, "retrain.py", "--generate", "0"],
                capture_output=True, text=True, timeout=7200,
            )
            if result.returncode == 0:
                retrain_status.update(
                    {
                        "last_retrain": __import__("datetime").datetime.now().isoformat(),
                        "last_retrain_success": True,
                        "total_retrains": retrain_status.get("total_retrains", 0) + 1,
                        "status": "success",
                    }
                )
                with open(LAST_RETRAIN_FILE, "w") as f:
                    __import__("json").dump(retrain_status, f)
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


async def start_auto_web_search(web_search_instance):
    """Запускает автопоиск слов в вебе."""
    if not AUTO_WEB_SEARCH_ENABLED or web_search_instance is None:
        return

    async def _run():
        try:
            from utils.auto_web_search import AutoWebSearch
            controller = AutoWebSearch(
                interval_seconds=AUTO_WEB_SEARCH_INTERVAL,
                batch_size=AUTO_WEB_SEARCH_BATCH_SIZE,
                min_word_length=AUTO_WEB_SEARCH_MIN_LENGTH,
                extract_depth=AUTO_WEB_SEARCH_EXTRACT_DEPTH,
                max_new_words_per_def=AUTO_WEB_SEARCH_MAX_NEW_WORDS,
                project_root=str(Path(__file__).resolve().parent.parent),
            )
            controller.web_search = web_search_instance

            # Запускаем в отдельном потоке без get_event_loop()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, controller.run_continuous)
        except Exception as e:
            logger.error(f"❌ Ошибка автопоиска слов: {e}")

    asyncio.create_task(_run())
