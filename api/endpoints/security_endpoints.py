# api/endpoints/security_endpoints.py — Эндпоинты безопасности

from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime

from services.security import (
    get_security_status, unblock_ip, blocked_ips, attack_store,
    attack_lock
)
from api.dependencies import get_retrain_token


async def security_status_endpoint() -> JSONResponse:
    """GET /security — Статус безопасности."""
    # Shiori scanner будет подключён через DI из main
    from main import shiori_scanner
    status = get_security_status()
    status["shiori_scanner"] = {
        "total_attacks": shiori_scanner.attack_stats["total_attacks"] if shiori_scanner else 0,
        "blocked_attacks": shiori_scanner.attack_stats["blocked_attacks"] if shiori_scanner else 0,
        "by_type": shiori_scanner.attack_stats["by_type"] if shiori_scanner else {},
        "by_severity": shiori_scanner.attack_stats["by_severity"] if shiori_scanner else {}
    }
    return JSONResponse(content=status)


async def unblock_ip_endpoint(ip: str, request: Request, retrain_token: str | None = Depends(get_retrain_token)) -> dict:
    """POST /security/unblock/{ip} — Разблокировать IP."""
    token = request.headers.get("X-Retrain-Token")
    if token != retrain_token:
        raise HTTPException(status_code=403, detail="Неверный токен")
    unblock_ip(ip)
    return {"status": "success", "message": f"IP {ip} разблокирован"}


async def reset_attacks_endpoint(request: Request, retrain_token: str | None = Depends(get_retrain_token)) -> dict:
    """POST /security/reset-attacks — Сбросить счётчик атак."""
    token = request.headers.get("X-Retrain-Token")
    if token != retrain_token:
        raise HTTPException(status_code=403, detail="Неверный токен")
    with attack_lock:
        attack_store.clear()
    return {"status": "success", "message": "Счётчик атак сброшен"}
