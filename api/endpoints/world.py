# api/endpoints/world.py — Эндпоинты WorldEngine

import logging
from fastapi import HTTPException
from services.model_loader import get_qwen_cache
from api.schemas import WorldCreateRequest, WorldCreateFromBooksRequest

logger = logging.getLogger("world")


def _get_bot_with_world():
    """Получает бота с проверкой WorldEngine."""
    local_bot = get_qwen_cache()
    if local_bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")
    if not hasattr(local_bot, 'world_engine') or not local_bot.world_engine_enabled:
        raise HTTPException(status_code=503, detail="WorldEngine не доступен")
    return local_bot


async def world_create(req: WorldCreateRequest) -> dict:
    """POST /world/create — Создать мир."""
    bot = _get_bot_with_world()
    try:
        result = bot.create_world(req.genre, req.tag)
        return {"status": "ok", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_create_from_books(req: WorldCreateFromBooksRequest) -> dict:
    """POST /world/create-from-books — Создать мир из книг."""
    bot = _get_bot_with_world()
    try:
        result = bot.create_world_from_books(req.genre, req.tag, req.book_titles)
        return {"status": "ok", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def worlds_list() -> dict:
    """GET /worlds — Список всех миров."""
    bot = get_qwen_cache()
    if bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")
    if not hasattr(bot, 'world_engine') or not bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}
    try:
        result = bot.get_all_worlds()
        return {"status": "ok", "worlds": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_info(world_name: str) -> dict:
    """GET /world/{world_name} — Информация о мире."""
    bot = get_qwen_cache()
    if bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")
    if not hasattr(bot, 'world_engine') or not bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}
    try:
        result = bot.get_world_info(world_name)
        return {"status": "ok", "info": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_generate_event(world_name: str) -> dict:
    """POST /world/{world_name}/event — Генерировать событие."""
    bot = _get_bot_with_world()
    try:
        result = bot.generate_event(world_name)
        return {"status": "ok", "event": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_get_events(world_name: str, limit: int = 10) -> dict:
    """GET /world/{world_name}/events — Последние события."""
    bot = get_qwen_cache()
    if bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")
    if not hasattr(bot, 'world_engine') or not bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}
    try:
        result = bot.get_world_events(world_name, limit)
        return {"status": "ok", "events": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_check_consistency(world_name: str) -> dict:
    """GET /world/{world_name}/consistency — Проверка лора."""
    bot = get_qwen_cache()
    if bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")
    if not hasattr(bot, 'world_engine') or not bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}
    try:
        result = bot.check_consistency(world_name)
        return {"status": "ok", "consistency": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_get_npc(world_name: str, npc_name: str) -> dict:
    """GET /world/{world_name}/npc/{npc_name} — Информация о NPC."""
    bot = get_qwen_cache()
    if bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")
    if not hasattr(bot, 'world_engine') or not bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}
    try:
        result = bot.get_npc_info(world_name, npc_name)
        return {"status": "ok", "npc": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_start_cycle() -> dict:
    """POST /world/start-cycle — Запуск фонового цикла."""
    bot = _get_bot_with_world()
    try:
        result = await bot.start_background_cycle()
        return {"status": "ok", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_stop_cycle() -> dict:
    """POST /world/stop-cycle — Остановка фонового цикла."""
    bot = _get_bot_with_world()
    try:
        result = bot.stop_background_cycle()
        return {"status": "ok", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def world_status() -> dict:
    """GET /world/status — Статус WorldEngine."""
    bot = get_qwen_cache()
    if bot is None:
        raise HTTPException(status_code=500, detail="Бот не загружен")
    if not hasattr(bot, 'world_engine') or not bot.world_engine_enabled:
        return {"status": "not available", "detail": "WorldEngine не доступен"}
    try:
        result = bot.get_world_status()
        return {"status": "ok", "status": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
