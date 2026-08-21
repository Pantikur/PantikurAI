# api/endpoints/girls.py — Эндпоинты оркестратора девочек

import logging
from fastapi import Request, HTTPException, Depends

from config import AUTO_GIRLS_ENABLED, GIRLS_TO_RUN
from api.dependencies import get_retrain_token

logger = logging.getLogger("girls")


async def girls_status() -> dict:
    """GET /girls — Статус оркестратора."""
    return {
        "status": "ok",
        "enabled": AUTO_GIRLS_ENABLED,
        "girls": GIRLS_TO_RUN,
        "count": len(GIRLS_TO_RUN),
        "message": "Девочки запущены автоматически при старте сервера"
    }


async def girls_restart(request: Request, retrain_token: str | None = Depends(get_retrain_token)) -> dict:
    """POST /girls/restart — Перезапуск девочек."""
    token = request.headers.get("X-Retrain-Token")
    if token != retrain_token:
        raise HTTPException(status_code=403, detail="Неверный токен")
    
    if not AUTO_GIRLS_ENABLED:
        return {"status": "ok", "detail": "Автозапуск девочек отключён"}
    
    logger.info("🔄 Перезапуск оркестратора девочек...")
    
    # Запуск оркестратора в фоне
    import subprocess
    import sys
    from pathlib import Path
    
    orchestrator_path = Path(__file__).resolve().parent.parent.parent / "orchestrator_v3.py"
    if orchestrator_path.exists():
        subprocess.Popen(
            [sys.executable, str(orchestrator_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    
    return {"status": "ok", "detail": f"Оркестратор перезапущен ({len(GIRLS_TO_RUN)} девочек)"}
