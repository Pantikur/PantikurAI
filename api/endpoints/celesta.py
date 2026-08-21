# api/endpoints/celesta.py — Эндпоинты системы Селеста

import logging
from fastapi import HTTPException, Depends

from api.dependencies import get_celesta_core
from api.schemas import (
    StudyRequest,
    CelestaConsequencesRequest,
    CelestaChatRequest,
    CelestaAutonomousRequest,
)

logger = logging.getLogger("celesta")


def _get_celesta(celesta_core):
    if celesta_core is None:
        raise HTTPException(status_code=503, detail="Celesta не загружена")
    return celesta_core


async def celesta_status(celesta_core=Depends(get_celesta_core)) -> dict:
    """GET /celesta/status"""
    local = _get_celesta(celesta_core)
    try:
        status = local.get_system_status()
        return {"status": "ok", "celesta": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_intimacy(celesta_core=Depends(get_celesta_core)) -> dict:
    """GET /celesta/intimacy"""
    local = _get_celesta(celesta_core)
    try:
        report = local.get_intimacy_report()
        return {"status": "ok", "intimacy": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_stage(stage: str, celesta_core=Depends(get_celesta_core)) -> dict:
    """GET /celesta/stage/{stage}"""
    local = _get_celesta(celesta_core)
    try:
        from celesta.intimacy_modules import IntimacyStage
        intimacy_stage = IntimacyStage(stage)
        details = local.get_stage_details(intimacy_stage)
        return {"status": "ok", "stage": details}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Неизвестный этап: {stage}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_consequences(req: CelestaConsequencesRequest, celesta_core=Depends(get_celesta_core)) -> dict:
    """POST /celesta/consequences"""
    local = _get_celesta(celesta_core)
    try:
        info = local.get_consequences_info(req.scenario)
        return {"status": "ok", "consequences": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_race(race: str, celesta_core=Depends(get_celesta_core)) -> dict:
    """GET /celesta/race/{race}"""
    local = _get_celesta(celesta_core)
    try:
        info = local.get_race_specific_info(race)
        return {"status": "ok", "race": race, "info": info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_study(req: StudyRequest, celesta_core=Depends(get_celesta_core)) -> dict:
    """POST /celesta/study"""
    local = _get_celesta(celesta_core)
    try:
        async def _run():
            await local.run_study_cycle(topics=req.topics, batch_size=req.batch_size)

        import asyncio
        asyncio.create_task(_run())
        return {"status": "ok", "message": "Цикл обучения запущен в фоне"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_chat(req: CelestaChatRequest, celesta_core=Depends(get_celesta_core)) -> dict:
    """POST /celesta/chat"""
    local = _get_celesta(celesta_core)
    try:
        response = local.chat_response(req.message)
        return {"status": "ok", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_learn(celesta_core=Depends(get_celesta_core)) -> dict:
    """POST /celesta/learn"""
    local = _get_celesta(celesta_core)
    try:
        local.start_intimacy_study()
        return {"status": "ok", "message": "Изучение интимной жизни начато"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_autonomous(req: CelestaAutonomousRequest, celesta_core=Depends(get_celesta_core)) -> dict:
    """POST /celesta/autonomous"""
    local = _get_celesta(celesta_core)
    try:
        local.start_autonomous_learning(interval_minutes=req.interval_minutes)
        return {"status": "ok", "message": f"Автономное обучение запущено (интервал: {req.interval_minutes} мин)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def celesta_self_improve(celesta_core=Depends(get_celesta_core)) -> dict:
    """POST /celesta/self-improve"""
    local = _get_celesta(celesta_core)
    try:
        async def _run():
            await local.self_improve()
        import asyncio
        asyncio.create_task(_run())
        return {"status": "ok", "message": "Саморазвитие запущено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
