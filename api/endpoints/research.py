# api/endpoints/research.py — Эндпоинты Research Monitor

import logging
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.responses import StreamingResponse
import time
import json

from api.dependencies import get_research_monitor

logger = logging.getLogger("research")


def _get_monitor(research_monitor):
    if research_monitor is None:
        raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
    return research_monitor


async def research_status(research_monitor=Depends(get_research_monitor)) -> dict:
    """GET /research/status"""
    monitor = _get_monitor(research_monitor)
    try:
        status = monitor.get_all_status()
        return {"status": "ok", "research": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def research_start(scientist: str, research_monitor=Depends(get_research_monitor)) -> dict:
    """POST /research/start/{scientist}"""
    monitor = _get_monitor(research_monitor)
    result = monitor.start_research(scientist)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["detail"])
    return result


async def research_stop(scientist: str, research_monitor=Depends(get_research_monitor)) -> dict:
    """POST /research/stop/{scientist}"""
    monitor = _get_monitor(research_monitor)
    result = monitor.stop_research(scientist)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["detail"])
    return result


async def research_summary(scientist: str, research_monitor=Depends(get_research_monitor)) -> dict:
    """GET /research/{scientist}/summary"""
    monitor = _get_monitor(research_monitor)
    summary = monitor.get_research_summary(scientist)
    if summary is None:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    return {"status": "ok", "scientist": scientist, "summary": summary}


async def research_events(scientist: str, research_monitor=Depends(get_research_monitor), limit: int = 50, event_type: Optional[str] = None) -> dict:
    """GET /research/{scientist}/events"""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    events = core.get_all_events(limit=limit, event_type=event_type)
    live_events = core.get_events(limit=10)
    return {"status": "ok", "scientist": scientist, "events": events, "live_events": live_events, "total_events": len(events)}


async def research_data(scientist: str, research_monitor=Depends(get_research_monitor)) -> dict:
    """GET /research/{scientist}/data — Данные Юи"""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    if scientist.lower() != 'yu':
        raise HTTPException(status_code=400, detail="Этот эндпоинт только для Юи")
    
    consciousness_models = core.get_consciousness_models(limit=20)
    embodiments = core.get_embodiments(limit=20)
    transfer_records = core.get_transfer_records(limit=20)
    
    return {
        "status": "ok", "scientist": scientist,
        "consciousness_models": consciousness_models,
        "embodiments": embodiments,
        "transfer_records": transfer_records,
        "count": {"models": len(consciousness_models), "embodiments": len(embodiments), "transfers": len(transfer_records)}
    }


async def research_logs(scientist: str, research_monitor=Depends(get_research_monitor), limit: int = 100) -> dict:
    """GET /research/{scientist}/logs"""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    logs = core.get_logs(limit=limit)
    return {"status": "ok", "scientist": scientist, "logs": logs, "count": len(logs)}


async def research_theories(scientist: str, research_monitor=Depends(get_research_monitor), limit: int = 20) -> dict:
    """GET /research/{scientist}/theories"""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    theories = core.get_theories(limit=limit)
    return {"status": "ok", "scientist": scientist, "theories": theories, "count": len(theories)}


async def research_calculations(scientist: str, research_monitor=Depends(get_research_monitor), limit: int = 20) -> dict:
    """GET /research/{scientist}/calculations"""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    calculations = core.get_calculations(limit=limit)
    return {"status": "ok", "scientist": scientist, "calculations": calculations, "count": len(calculations)}


async def research_papers(scientist: str, research_monitor=Depends(get_research_monitor), limit: int = 20) -> dict:
    """GET /research/{scientist}/papers"""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    papers = core.get_papers(limit=limit)
    return {"status": "ok", "scientist": scientist, "papers": papers, "count": len(papers)}


async def research_history(scientist: str, research_monitor=Depends(get_research_monitor), limit: int = 50) -> dict:
    """GET /research/{scientist}/history"""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    history = core.get_research_history(limit=limit)
    return {"status": "ok", "scientist": scientist, "history": history, "count": len(history)}


async def research_core_status(scientist: str, research_monitor=Depends(get_research_monitor)) -> dict:
    """GET /research/{scientist}/status"""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    return {"status": "ok", "scientist": scientist, "core": core.get_status()}


def research_live(scientist: str, research_monitor=Depends(get_research_monitor)):
    """GET /research/live/{scientist} — SSE поток событий."""
    monitor = _get_monitor(research_monitor)
    core = monitor.get_core(scientist)
    if not core:
        raise HTTPException(status_code=404, detail=f"Ядро '{scientist}' не найдено")
    
    def event_stream():
        while True:
            try:
                events = core.get_events(limit=10)
                for event in events:
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                
                status = core.get_status()
                status_event = {"type": "status", "scientist": scientist, "data": status}
                yield f"data: {json.dumps(status_event, ensure_ascii=False)}\n\n"
                time.sleep(2)
            except GeneratorExit:
                break
            except Exception as e:
                error_event = {"type": "error", "scientist": scientist, "data": {"error": str(e)}}
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
                time.sleep(5)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )


def research_live_all(research_monitor=Depends(get_research_monitor)):
    """GET /research/live/all — SSE поток всех ядер."""
    monitor = _get_monitor(research_monitor)
    
    def event_stream():
        while True:
            try:
                for name, core in monitor.cores.items():
                    events = core.get_events(limit=5)
                    for event in events:
                        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                
                status = monitor.get_all_status()
                status_event = {"type": "status", "data": status}
                yield f"data: {json.dumps(status_event, ensure_ascii=False)}\n\n"
                time.sleep(2)
            except GeneratorExit:
                break
            except Exception as e:
                error_event = {"type": "error", "data": {"error": str(e)}}
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
                time.sleep(5)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
    )
