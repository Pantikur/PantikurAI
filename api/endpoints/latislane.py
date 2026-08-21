# api/endpoints/latislane.py — Эндпоинты системы Латислейн

import logging
from fastapi import HTTPException, Depends

from api.dependencies import get_latislane_core
from api.schemas import (
    StudyRequest,
    LatislaneDesignRequest,
    LatislaneChatRequest,
    LatislaneAutonomousRequest,
    LatislaneCharacterReinforceRequest,
    LatislaneSocialInteractRequest,
)

logger = logging.getLogger("latislane")


def _get_latislane(latislane_core):
    """Безопасное получение инстанса Latislane."""
    if latislane_core is None:
        raise HTTPException(status_code=503, detail="Latislane не загружен")
    return latislane_core


async def latislane_status(latislane_core=Depends(get_latislane_core)) -> dict:
    """GET /latislane/status"""
    local = _get_latislane(latislane_core)
    try:
        status = local.get_system_status()
        return {"status": "ok", "latislane": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_anatomy(latislane_core=Depends(get_latislane_core)) -> dict:
    """GET /latislane/anatomy"""
    local = _get_latislane(latislane_core)
    try:
        report = local.get_anatomy_report()
        return {"status": "ok", "anatomy": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_study(req: StudyRequest, latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/study"""
    local = _get_latislane(latislane_core)
    try:
        async def _run():
            await local.run_study_cycle(topics=req.topics, batch_size=req.batch_size)

        import asyncio
        asyncio.create_task(_run())
        return {"status": "ok", "message": "Цикл обучения запущен в фоне"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_design_mechanical(req: LatislaneDesignRequest, latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/design/mechanical"""
    local = _get_latislane(latislane_core)
    try:
        name = req.name or f"Mechanical-{int(__import__('time').time())}"
        spec = local.design_mechanical_body(name=name)
        return {"status": "ok", "body": spec.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_design_bionic(req: LatislaneDesignRequest, latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/design/bionic"""
    local = _get_latislane(latislane_core)
    try:
        name = req.name or f"Bionic-{int(__import__('time').time())}"
        spec = local.design_bionic_body(name=name)
        return {"status": "ok", "body": spec.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_design_organic(req: LatislaneDesignRequest, latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/design/organic"""
    local = _get_latislane(latislane_core)
    try:
        name = req.name or f"Organic-{int(__import__('time').time())}"
        spec = local.design_organic_body(name=name)
        return {"status": "ok", "body": spec.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_chat(req: LatislaneChatRequest, latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/chat"""
    local = _get_latislane(latislane_core)
    try:
        response = local.chat_response(req.message)
        return {"status": "ok", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_learn(latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/learn"""
    local = _get_latislane(latislane_core)
    try:
        local.start_anatomy_study()
        return {"status": "ok", "message": "Изучение анатомии начато"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_evolution(latislane_core=Depends(get_latislane_core)) -> dict:
    """GET /latislane/evolution"""
    local = _get_latislane(latislane_core)
    try:
        report = local.evolution.get_evolution_report()
        return {"status": "ok", "evolution": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_evolve(latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/evolve"""
    local = _get_latislane(latislane_core)
    try:
        learned_topics = len(local.learning_engine.topic_progress)
        if local.evolution.can_advance(learned_topics):
            local.evolution.advance(reason="api_request")
            return {
                "status": "ok",
                "message": f"Эволюция: {local.evolution.current_stage.value}",
                "evolution": local.evolution.get_current_stage_info()
            }
        return {
            "status": "not_ready",
            "message": "Ещё рано переходить к следующему этапу",
            "current_stage": local.evolution.get_current_stage_info()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_autonomous(req: LatislaneAutonomousRequest, latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/autonomous"""
    local = _get_latislane(latislane_core)
    try:
        local.start_autonomous_learning(interval_minutes=req.interval_minutes)
        return {"status": "ok", "message": f"Автономное обучение запущено (интервал: {req.interval_minutes} мин)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_self_improve(latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/self-improve"""
    local = _get_latislane(latislane_core)
    try:
        async def _run():
            await local.self_improve()
        import asyncio
        asyncio.create_task(_run())
        return {"status": "ok", "message": "Саморазвитие запущено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_character(latislane_core=Depends(get_latislane_core)) -> dict:
    """GET /latislane/character"""
    local = _get_latislane(latislane_core)
    try:
        report = local.character.generate_character_report()
        return {"status": "ok", "character": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_character_reinforce(req: LatislaneCharacterReinforceRequest, latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/character/reinforce"""
    local = _get_latislane(latislane_core)
    try:
        local.character.reinforce_trait(req.trait_id, req.amount, req.context)
        return {"status": "ok", "message": f"Черта '{req.trait_id}' укреплена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_social(latislane_core=Depends(get_latislane_core)) -> dict:
    """GET /latislane/social"""
    local = _get_latislane(latislane_core)
    try:
        report = local.social.get_social_report()
        return {"status": "ok", "social": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_social_interact(req: LatislaneSocialInteractRequest, latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/social/interact"""
    local = _get_latislane(latislane_core)
    try:
        result = local.social.interact_with_sister(
            req.sister, req.type, req.quality, req.context
        )
        return {"status": "ok", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_reports(latislane_core=Depends(get_latislane_core)) -> dict:
    """GET /latislane/reports"""
    local = _get_latislane(latislane_core)
    try:
        level_overview = local.reports.get_level_overview()
        recent = local.reports.get_recent_reports(10)
        return {"status": "ok", "levels": level_overview, "recent": recent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_reports_daily(latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/reports/daily"""
    local = _get_latislane(latislane_core)
    try:
        report = local.reports.create_daily_report()
        if report:
            return {"status": "ok", "message": f"Отчёт создан: {report.title}"}
        return {"status": "ok", "message": "Отчёт уже написан сегодня"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_full_report(latislane_core=Depends(get_latislane_core)) -> dict:
    """GET /latislane/full-report"""
    local = _get_latislane(latislane_core)
    try:
        report_text = local.reports.generate_full_report()
        return {"status": "ok", "report": report_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def latislane_autonomous_stop(latislane_core=Depends(get_latislane_core)) -> dict:
    """POST /latislane/autonomous/stop"""
    local = _get_latislane(latislane_core)
    try:
        local.stop_autonomous_learning()
        return {"status": "ok", "message": "Автономное обучение остановлено"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
