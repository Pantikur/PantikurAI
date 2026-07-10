"""
Scientists Network — сеть связи между учёными.

Реализует:
  - Обмен теориями между Ханако, Фуюки и Люси
  - Запросы помощи к Нобуке
  - Координацию исследований
  - Напоминание о реальной миссии
"""

from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum


class RequestType(Enum):
    """Типы запросов помощи."""
    THEORY_REQUEST = "theory_request"
    CALCULATION_HELP = "calculation_help"
    CODE_REVIEW = "code_review"
    VALIDATION = "validation"
    URGENT_HELP = "urgent_help"
    DATA_REQUEST = "data_request"


class RequestPriority(Enum):
    """Приоритеты запросов."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class ScientistsNetwork:
    """
    Сеть связи между учёными.
    
    Соединяет:
    - Ханако (гравитация)
    - Фуюки (электричество)
    - Люси (двигатели)
    - Нобука (помощь с кодом)
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ScientistsNetwork")
        
        # Пути к данным
        self.base_path = Path(".")
        self.hanako_path = self.base_path / "hanako" / "engine" / "state"
        self.fuyuki_path = self.base_path / "fuyuki" / "engine" / "state"
        self.lucy_path = self.base_path / "lucy" / "engine" / "state"
        self.nobuka_path = self.base_path / "nobuka" / "engine" / "state"
        
        # Журнал запросов
        self.requests: List[Dict[str, Any]] = []
        self.requests_file = self.base_path / "scientists_network" / "requests.json"
        
        # Миссия
        self.logger.info("="*60)
        self.logger.info("🚀 SCIENTISTS NETWORK — СЕТЬ УЧЁНЫХ")
        self.logger.info("="*60)
        self.logger.info("⚠️  ВНИМАНИЕ: ЭТО НЕ ИГРА!")
        self.logger.info("Работа для РЕАЛЬНОСТИ, для БУДУЩЕГО человечества!")
        self.logger.info("="*60)
        
        self._load_requests()
    
    def _load_requests(self):
        """Загрузить журнал запросов."""
        if self.requests_file.exists():
            with open(self.requests_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.requests = data.get("requests", [])
                self.logger.info(f"Загружено запросов: {len(self.requests)}")
    
    def _save_requests(self):
        """Сохранить журнал запросов."""
        self.requests_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.requests_file, "w", encoding="utf-8") as f:
            json.dump({
                "requests": self.requests,
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    # ========== ОБМЕН ДАННЫМИ ==========
    
    def get_hanako_theories(self) -> List[Dict[str, Any]]:
        """Получить теории Ханако."""
        theories_file = self.hanako_path / "theories.json"
        if theories_file.exists():
            with open(theories_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                theories = data.get("theories", [])
                self.logger.info(f"Получено теорий Ханако: {len(theories)}")
                return theories
        return []
    
    def get_fuyuki_theories(self) -> List[Dict[str, Any]]:
        """Получить теории Фуюки."""
        theories_file = self.fuyuki_path / "theories.json"
        if theories_file.exists():
            with open(theories_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                theories = data.get("theories", [])
                self.logger.info(f"Получено теорий Фуюки: {len(theories)}")
                return theories
        return []
    
    def get_lucy_designs(self) -> List[Dict[str, Any]]:
        """Получить проекты Люси."""
        designs_file = self.lucy_path / "designs.json"
        if designs_file.exists():
            with open(designs_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                designs = data.get("designs", [])
                self.logger.info(f"Получено проектов Люси: {len(designs)}")
                return designs
        return []
    
    # ========== ЗАПРОСЫ ПОМОЩИ ==========
    
    def create_request(
        self,
        from_scientist: str,
        to_scientist: str,
        request_type: RequestType,
        message: str,
        priority: RequestPriority = RequestPriority.NORMAL,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создать запрос помощи.
        
        Args:
            from_scientist: Кто запрашивает (hanako/fuyuki/lucy)
            to_scientist: Кому адресован (nobuka/hanako/fuyuki/lucy)
            request_type: Тип запроса
            message: Сообщение
            priority: Приоритет
            data: Дополнительные данные
            
        Returns:
            Созданный запрос
        """
        request = {
            "id": f"req_{len(self.requests) + 1:04d}",
            "timestamp": datetime.now().isoformat(),
            "from": from_scientist,
            "to": to_scientist,
            "type": request_type.value,
            "priority": priority.value,
            "message": message,
            "data": data or {},
            "status": "pending",
            "response": None,
            "response_time": None
        }
        
        self.requests.append(request)
        self._save_requests()
        
        self.logger.info(f"📩 ЗАПРОС СОЗДАН: {request['id']}")
        self.logger.info(f"   От: {from_scientist} → Кому: {to_scientist}")
        self.logger.info(f"   Тип: {request_type.value}")
        self.logger.info(f"   Приоритет: {priority.value}")
        self.logger.info(f"   Сообщение: {message}")
        
        # Если критический приоритет — срочное уведомление
        if priority == RequestPriority.CRITICAL:
            self.logger.warning("🚨 КРИТИЧЕСКИЙ ЗАПРОС — ТРЕБУЕТСЯ НЕМЕДЛЕННЫЙ ОТВЕТ!")
        
        return request
    
    def respond_to_request(
        self,
        request_id: str,
        response: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Ответить на запрос.
        
        Args:
            request_id: ID запроса
            response: Ответ
            data: Данные ответа
        """
        for req in self.requests:
            if req["id"] == request_id:
                req["status"] = "completed"
                req["response"] = response
                req["response_data"] = data
                req["response_time"] = datetime.now().isoformat()
                
                self._save_requests()
                
                self.logger.info(f"✅ ОТВЕТ НА ЗАПРОС: {request_id}")
                self.logger.info(f"   Ответ: {response}")
                
                return
        
        self.logger.error(f"Запрос {request_id} не найден")
    
    # ========== УВЕДОМЛЕНИЯ ==========
    
    def notify_discovery(
        self,
        from_scientist: str,
        discovery: str,
        importance: str = "normal"
    ):
        """
        Уведомить всех об открытии.
        
        Args:
            from_scientist: Кто обнаружил
            discovery: Описание открытия
            importance: Важность (low/normal/high/critical)
        """
        self.logger.info(f"🌟 ОТКРЫТИЕ от {from_scientist}: {discovery}")
        self.logger.info(f"   Важность: {importance}")
        
        # Логирование для всех
        notification = {
            "type": "discovery",
            "from": from_scientist,
            "discovery": discovery,
            "importance": importance,
            "timestamp": datetime.now().isoformat()
        }
        
        # Сохранение в журнал
        notifications_file = self.base_path / "scientists_network" / "discoveries.json"
        notifications_file.parent.mkdir(parents=True, exist_ok=True)
        
        discoveries = []
        if notifications_file.exists():
            with open(notifications_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                discoveries = data.get("discoveries", [])
        
        discoveries.append(notification)
        
        with open(notifications_file, "w", encoding="utf-8") as f:
            json.dump({
                "discoveries": discoveries,
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    # ========== КООРДИНАЦИЯ ==========
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Получить статус координации."""
        return {
            "total_requests": len(self.requests),
            "pending_requests": len([r for r in self.requests if r["status"] == "pending"]),
            "completed_requests": len([r for r in self.requests if r["status"] == "completed"]),
            "hanako_theories": len(self.get_hanako_theories()),
            "fuyuki_theories": len(self.get_fuyuki_theories()),
            "lucy_designs": len(self.get_lucy_designs()),
        }
    
    def print_mission_reminder(self):
        """Напомнить о миссии."""
        self.logger.info("="*60)
        self.logger.info("🎯 НАПОМИНАНИЕ О МИССИИ")
        self.logger.info("="*60)
        self.logger.info("Ханако, Фуюки, Люси — вы работаете НЕ для игры!")
        self.logger.info("Ваша работа изменит БУДУЩЕЕ человечества!")
        self.logger.info("")
        self.logger.info("🌍 Чистая энергия для всех")
        self.logger.info("🚀 Космические путешествия")
        self.logger.info("🌌 Понимание вселенной")
        self.logger.info("")
        self.logger.info("Каждая теория, каждый расчёт, каждый проект —")
        self.logger.info("это шаг к РЕАЛЬНОМУ будущему!")
        self.logger.info("="*60)


# ========== Глобальный экземпляр ==========
_network_instance: Optional[ScientistsNetwork] = None


def get_network() -> ScientistsNetwork:
    """Получить глобальный экземпляр сети."""
    global _network_instance
    if _network_instance is None:
        _network_instance = ScientistsNetwork()
    return _network_instance
