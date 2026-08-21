# api/endpoints/network.py — Эндпоинты Scientists Network

import logging
from typing import Optional
from fastapi import HTTPException, Depends

from api.dependencies import get_research_monitor
from api.schemas import NetworkSendRequest

logger = logging.getLogger("network")


def _get_monitor(research_monitor):
    if research_monitor is None:
        raise HTTPException(status_code=503, detail="ResearchMonitor не загружен")
    return research_monitor


async def network_status(research_monitor=Depends(get_research_monitor)) -> dict:
    """GET /network/status"""
    monitor = _get_monitor(research_monitor)
    try:
        stats = monitor.network.get_stats()
        return {"status": "ok", "network": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def network_history(research_monitor=Depends(get_research_monitor), limit: int = 50, sender: Optional[str] = None) -> dict:
    """GET /network/history"""
    monitor = _get_monitor(research_monitor)
    try:
        messages = monitor.network.get_message_history(limit=limit, sender=sender)
        return {"status": "ok", "messages": messages, "count": len(messages)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def network_send(req: NetworkSendRequest, research_monitor=Depends(get_research_monitor)) -> dict:
    """POST /network/send"""
    monitor = _get_monitor(research_monitor)
    try:
        from scientists_network.network import Message, MessageType, RequestPriority
        msg_type = MessageType(req.message_type)
        msg_priority = RequestPriority(req.priority)

        message = Message(
            message_type=msg_type, sender=req.sender, recipient=req.recipient,
            content=req.content, priority=msg_priority
        )

        success = monitor.network.send_message(message)
        if success:
            return {"status": "ok", "message": "Сообщение отправлено", "sender": req.sender, "recipient": req.recipient}
        raise HTTPException(status_code=400, detail="Не удалось отправить сообщение")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка типа сообщения: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
