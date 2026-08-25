# services/retrain_service.py — Сервис ретраина модели

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from config import RETRAIN_TOKEN, BASE_DIR, LAST_RETRAIN_FILE, retrain_status
from services.model_loader import load_qwen_model

logger = logging.getLogger("retrain_service")


def run_retrain():
    """Запускает retrain.py в фоне с перезагрузкой модели.

    Возвращает True если успешно, False если ошибка.
    """
    if not RETRAIN_TOKEN:
        logger.error("❌ RETRAIN_TOKEN не задан")
        return False

    lock = __import__("threading", fromlist=["RLock"]).RLock()
    if not lock.acquire(blocking=False):
        logger.warning("🔄 Ретраин уже запущен")
        return False

    try:
        logger.info("🎂 Запускаю ретраин...")
        result = subprocess.run(
            [sys.executable, "retrain.py"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode == 0:
            logger.info("🎉 Ретраин завершён!")
            try:
                from services.model_init import _qwen_cache_ref

                _qwen_cache_ref[0] = None  # type: ignore[index]
                qwen_model = load_qwen_model()
                with lock:
                    _qwen_cache_ref[0] = qwen_model  # type: ignore[index]
            except Exception as e:
                logger.error(f"❌ Не удалось перезагрузить модель: {e}")

            retrain_status.update(
                {
                    "last_retrain": datetime.now().isoformat(),
                    "last_retrain_success": True,
                    "total_retrains": retrain_status.get("total_retrains", 0) + 1,
                    "status": "success",
                }
            )
            with open(LAST_RETRAIN_FILE, "w") as f:
                json.dump(retrain_status, f)
            return True
        else:
            logger.error(f"❌ Ошибка ретраина: {result.stderr}")
            retrain_status["status"] = "error"
            return False
    except subprocess.TimeoutExpired:
        logger.error("⏰ Превышен лимит времени (10 мин)")
        retrain_status["status"] = "error"
        return False
    except Exception as e:
        logger.error(f"💥 Ошибка запуска: {e}")
        retrain_status["status"] = "error"
        return False
    finally:
        lock.release()
