"""
Интеграция Сидни с Wuglarst.

Позволяет Сидни:
- Отправлять состояние в Wuglarst
- Получать события от других девочек
- Работать через WebSocket
- Поддерживать постоянный онлайн
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.request import urlopen, Request
from urllib.error import URLError

logger = logging.getLogger("sidney.wuglarst")


class WuglarstClient:
    """Клиент для взаимодействия с Wuglarst сервером."""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.ws_url = f"ws://{host}:{port}/ws"
        
        self.connected = False
        self.scientist_name = "Сидни"
        self._heartbeat_task = None
        self._running = False
        
        logger.info(f"🔌 WuglarstClient инициализирован (port={port})")
    
    def _api_post(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Отправка POST запроса к API."""
        try:
            url = f"{self.base_url}{endpoint}"
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            req = Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
            
            with urlopen(req, timeout=5) as response:
                return response.status == 200
                
        except Exception as e:
            logger.debug(f"API ошибка: {e}")
            return False
    
    def _api_get(self, endpoint: str) -> Optional[Dict]:
        """Отправка GET запроса к API."""
        try:
            url = f"{self.base_url}{endpoint}"
            req = Request(url, method='GET')
            
            with urlopen(req, timeout=5) as response:
                return json.loads(response.read().decode())
                
        except Exception as e:
            logger.debug(f"API ошибка: {e}")
            return None
    
    def update_status(self, status: str = "working", current_task: str = "",
                     personality: Optional[Dict] = None,
                     knowledge_levels: Optional[Dict] = None,
                     position: Optional[tuple] = None):
        """Обновление состояния в Wuglarst."""
        data = {
            "name": self.scientist_name,
            "avatar": "🎮",
            "status": status,
            "current_task": current_task or "Игровой движок",
            "personality": personality or {
                "перфекционизм": 75,
                "инновационность": 80,
                "аналитичность": 85,
                "коллаборативность": 90
            },
            "last_activity": datetime.now().isoformat(),
            "x": position[0] if position else 500,
            "y": position[1] if position else 400,
            "knowledge_levels": knowledge_levels or {},
            "autonomy_level": "L3",
            "engines_active": 8
        }
        
        success = self._api_post("/api/scientist/Сидни/update", data)
        if success:
            logger.debug(f"📡 Статус отправлен: {status}")
        return success
    
    def mark_online(self):
        """Отметить себя онлайн."""
        return self._api_post("/api/scientist/Сидни/online", {})
    
    def mark_offline(self):
        """Отметить себя оффлайн."""
        return self._api_post("/api/scientist/Сидни/offline", {})
    
    def add_event(self, event_type: str, message: str):
        """Добавить событие в журнал."""
        return self._api_post(f"/api/scientist/Сидни/event", {
            "type": event_type,
            "message": message
        })
    
    def get_status(self) -> Optional[Dict]:
        """Получить статус системы."""
        return self._api_get("/api/status")
    
    def get_health(self) -> Optional[Dict]:
        """Получить здоровье сервера."""
        return self._api_get("/health")
    
    async def start_heartbeat(self, interval: int = 60):
        """Запуск heartbeat для поддержания онлайн статуса."""
        self._running = True
        
        while self._running:
            try:
                self.mark_online()
                logger.debug(f"💓 Heartbeat отправлен")
            except Exception as e:
                logger.error(f"❌ Heartbeat ошибка: {e}")
            
            await asyncio.sleep(interval)
    
    def stop_heartbeat(self):
        """Остановка heartbeat."""
        self._running = False
        self.mark_offline()
        logger.info("💓 Heartstop остановлен")
    
    def connect_to_sisters(self):
        """Подключение к девочкам через Wuglarst."""
        status = self.get_status()
        if not status:
            logger.error("❌ Не удалось получить статус")
            return {}
        
        scientists = status.get("scientists", {})
        online_sisters = {
            name: sci for name, sci in scientists.items()
            if sci.get("status") != "offline" and name != "Сидни"
        }
        
        logger.info(f"👭 Подключено к {len(online_sisters)} девочкам через Wuglarst")
        return online_sisters


# =====================================================================
#  ИНТЕГРАЦИЯ С СИДНИ
# =====================================================================

class SidneyWuglarstIntegration:
    """Полная интеграция Сидни с Wuglarst."""
    
    def __init__(self, sidney_core, host: str = "localhost", port: int = 8001):
        self.sidney = sidney_core
        self.client = WuglarstClient(host, port)
        self.last_sync = 0
        self.sync_interval = 30  # Секунд
        
        logger.info("🔗 Интеграция Сидни-Wuglarst создана")
    
    def sync_status(self):
        """Синхронизация состояния Сидни с Wuglarst."""
        now = time.time()
        if now - self.last_sync < self.sync_interval:
            return
        
        self.last_sync = now
        
        # Получаем статус Сидни
        status = self.sidney.get_status()
        
        # Обновляем в Wuglarst
        self.client.update_status(
            status=status.get("engines", {}).get("is_running", False) and "working" or "idle",
            current_task=f"Цикл {status.get('stats', {}).get('total_cycles', 0)} | Знаний: {status.get('overall_knowledge_level', 0)}",
            personality=status.get("character", {}).get("traits", {}),
            knowledge_levels=status.get("knowledge", {})
        )
        
        logger.debug("🔄 Статус Сидни синхронизирован")
    
    def broadcast_engine_event(self, event_type: str, data: Dict):
        """Отправка события от движка в Wuglarst."""
        message = f"🎮 Движок {event_type}: {json.dumps(data, ensure_ascii=False)[:100]}"
        self.client.add_event("engine_event", message)
        logger.info(f"📡 Событие движка: {event_type}")
    
    def receive_sister_message(self, sister_name: str, message: str):
        """Получение сообщения от девочки."""
        self.client.add_event("sister_message", f"💬 {sister_name}: {message}")
        logger.info(f"💬 Сообщение от {sister_name}: {message}")
    
    def start(self):
        """Запуск интеграции."""
        logger.info("🚀 Интеграция запущена")
        
        # Отметить онлайн
        self.client.mark_online()
        
        # Подключиться к девочкам
        sisters = self.client.connect_to_sisters()
        logger.info(f"👭 Найдено {len(sisters)} девочек онлайн")
    
    def stop(self):
        """Остановка интеграции."""
        self.client.stop_heartbeat()
        logger.info("⏹️ Интеграция остановлена")
