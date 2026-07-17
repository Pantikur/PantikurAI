"""
Интеграция Наото с Вугларст (Wuglarst).
Позволяет Наото отправлять состояние в визуальное пространство.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("NaotoWuglarst")


class WuglarstClient:
    """Клиент для отправки данных в Вугларст."""

    def __init__(self, api_url: str = "http://localhost:8001"):
        self.api_url = api_url.rstrip('/')
        self.http_client = httpx.AsyncClient(timeout=10.0)

    async def update_status(
        self,
        name: str,
        status: str,
        current_task: str,
        personality: Optional[Dict[str, float]] = None,
        position: Optional[Dict[str, int]] = None,
    ):
        """Отправляет обновление состояния в Вугларст."""
        try:
            data = {
                "name": name,
                "avatar": "📚",
                "status": status,
                "current_task": current_task,
                "personality": personality or {},
                "position": position or {"x": 200, "y": 300},
            }

            response = await self.http_client.post(
                f"{self.api_url}/api/scientist/{name}/update",
                json=data,
            )

            if response.status_code == 200:
                logger.info(f"✅ Наото → Вугларст: {current_task}")
            else:
                logger.warning(f"⚠️ Ошибка отправки: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Вугларст: {e}")

    async def add_event(self, event_type: str, message: str):
        """Добавляет событие в журнал Вугларст."""
        try:
            await self.http_client.post(
                f"{self.api_url}/api/scientist/Наото/event",
                json={
                    "type": event_type,
                    "message": message,
                },
            )
        except Exception as e:
            logger.error(f"❌ Ошибка добавления события: {e}")

    async def close(self):
        """Закрытие клиента."""
        await self.http_client.aclose()


# Глобальный экземпляр
wuglarst_client: Optional[WuglarstClient] = None


def get_wuglarst_client() -> WuglarstClient:
    """Получение глобального клиента Вугларст."""
    global wuglarst_client
    if wuglarst_client is None:
        wuglarst_client = WuglarstClient()
    return wuglarst_client


async def shutdown_wuglarst():
    """Закрытие клиента."""
    global wuglarst_client
    if wuglarst_client:
        await wuglarst_client.close()
        wuglarst_client = None
