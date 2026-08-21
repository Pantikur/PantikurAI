# api/endpoints/retrain.py — Эндпоинты обучения модели

import subprocess
import sys
import json
import logging
import asyncio
from datetime import datetime
from fastapi import Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from config import AUTO_RETRAIN_ENABLED, AUTO_RETRAIN_INTERVAL, LAST_RETRAIN_FILE, retrain_status
from api.dependencies import get_retrain_token, get_gigachat_token, get_base_dir

logger = logging.getLogger("retrain")


async def manual_retrain(request: Request) -> dict:
    """POST /retrain/manual — Ручной запуск обучения модели."""
    if retrain_status["status"] == "running":
        raise HTTPException(status_code=409, detail="Обучение уже запущено")
    
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
            raise HTTPException(status_code=500, detail=f"Ошибка обучения: {result.stderr[:500]}")
            
    except subprocess.TimeoutExpired:
        retrain_status["status"] = "error"
        raise HTTPException(status_code=504, detail="Таймаут обучения (2 часа)")
    except Exception as e:
        retrain_status["status"] = "error"
        raise HTTPException(status_code=500, detail=str(e))


async def retrain_status_endpoint() -> dict:
    """GET /retrain/status — Статус обучения."""
    return {
        "status": retrain_status["status"],
        "last_retrain": retrain_status["last_retrain"],
        "last_retrain_success": retrain_status["last_retrain_success"],
        "total_retrains": retrain_status["total_retrains"],
        "auto_retrain_enabled": AUTO_RETRAIN_ENABLED,
        "interval_seconds": AUTO_RETRAIN_INTERVAL,
        "interval_human": f"{AUTO_RETRAIN_INTERVAL // 3600} часа(ов)"
    }


async def enrich_gigachat(request: Request, gigachat_token: str | None = Depends(get_gigachat_token), retrain_token_val: str | None = Depends(get_retrain_token)) -> dict:
    """POST /enrich — Сбор данных от GigaChat."""
    if not gigachat_token:
        raise HTTPException(status_code=503, detail="GIGACHAT_TOKEN не задан")
    
    token = request.headers.get("X-Retrain-Token")
    if token != retrain_token_val:
        raise HTTPException(status_code=403, detail="Неверный токен")
    
    try:
        from bot_learns_from_gigachat import generate_self_teaching_dialogs
        logger.info("🤖 Запускаю self-teaching от GigaChat...")
        generate_self_teaching_dialogs(n=3)
        return {"status": "enriched", "detail": "Диалоги добавлены в conversations.json"}
    except Exception as e:
        logger.error(f"❌ Ошибка enrichment: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка enrichment: {e}")


def run_retrain_sync(chatbot_ref, CHATBOT_LOCK, BASE_DIR, retrain_token: str | None):
    """Запуск retrain.py в фоне с блокировкой."""
    global chatbot
    from services.model_loader import load_qwen_model
    
    if not retrain_token:
        logger.error("❌ RETRAIN_TOKEN не задан — ретраин недоступен")
        return
    
    import threading
    if not CHATBOT_LOCK.acquire(blocking=False):
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
            try:
                _qwen_cache = None
                qwen_model = load_qwen_model()
                with CHATBOT_LOCK:
                    chatbot_ref[0] = qwen_model
                logger.info("🔁 Qwen2.5-3B перезагружена после обучения")
            except Exception as e:
                logger.error(f"❌ Не удалось перезагрузить Qwen2.5-3B: {e}")
        else:
            logger.error(f"❌ Ошибка ретраина: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("⏰ Превышен лимит времени (10 мин)")
    except Exception as e:
        logger.error(f"💥 Ошибка запуска: {e}")
    finally:
        CHATBOT_LOCK.release()


async def trigger_retrain(request: Request, background_tasks: BackgroundTasks, chatbot_ref, CHATBOT_LOCK, base_dir: str = Depends(get_base_dir), retrain_token_val: str | None = Depends(get_retrain_token)) -> dict:
    """POST /retrain — Запуск ретраина в фоне."""
    if not retrain_token_val:
        raise HTTPException(status_code=503, detail="Ретраин отключен (нет RETRAIN_TOKEN)")
    
    token = request.headers.get("X-Retrain-Token")
    if token != retrain_token_val:
        raise HTTPException(status_code=403, detail="Неверный токен 🎂")
    
    logger.info("🔧 Запрос на ретраин получен — ставим в фон")
    background_tasks.add_task(run_retrain_sync, chatbot_ref, CHATBOT_LOCK, base_dir, retrain_token_val)
    return {"status": "retrain_started", "detail": "Обучение запущено в фоне!"}
