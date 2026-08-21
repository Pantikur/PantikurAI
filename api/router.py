# api/router.py — FastAPI Router с конфигурацией маршрутов

# До рефакторинга: 657 строк дублирующегося кода
# После рефакторинга: ~30 строк — все маршруты в router_config.py

from fastapi import APIRouter, Depends
from api.dependencies import (
    get_latislane_core, get_LATISLANE_LOCK,
    get_celesta_core, get_CELESTA_LOCK,
    get_research_monitor,
)
from api.router_config import ROUTES

router = APIRouter()

# === Регистрация всех маршрутов из конфигурации ===
for route_config in ROUTES:
    dependencies = route_config.get("dependencies", [])
    
    router.add_api_route(
        path=route_config["path"],
        endpoint=route_config["endpoint"],
        methods=route_config["methods"],
        dependencies=[Depends(d) for d in dependencies],
    )
