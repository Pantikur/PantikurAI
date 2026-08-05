"""
Коммуникация Наото с другими AI-агентами.
"""

from __future__ import annotations

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from naoto.engine.config import NaotoConfig


class NaotoCommunication:
    """
    Коммуникация Наото с другими AI-агентами через Scientists Network.
    
    Поддерживает:
    - Приём запросов от сестёр
    - Отправку результатов литературного анализа
    - Обмен знаниями о литературе
    - Участие в совместных проектах
    """

    def __init__(self, config: NaotoConfig):
        self.config = config
        self.logger = logging.getLogger("NaotoCommunication")
        
        # Журнал взаимодействий
        self.interaction_log: List[Dict[str, Any]] = []
        
        # Статусы сестёр
        self.sister_status: Dict[str, Dict[str, Any]] = {
            sister: {
                "status": "unknown",
                "last_contact": None,
                "requests_sent": 0,
                "requests_received": 0
            }
            for sister in self.config.sister_names
        }
        
        # Загрузка журнала
        self._load_interaction_log()

    # ================================================================
    #  ИНИЦИАЛИЗАЦИЯ
    # ================================================================

    def init_network(self) -> None:
        """Инициализирует Scientists Network."""
        if not self.config.communication_enabled:
            self.logger.info("⏭️ Коммуникация отключена в конфигурации")
            return
        
        if not self.config.scientists_network_enabled:
            self.logger.info("⏭️ Scientists Network отключён в конфигурации")
            return
        
        self.logger.info("📡 Инициализация Scientists Network")
        
        # Установка статусов сестёр
        for sister in self.sister_status:
            self.sister_status[sister]["status"] = "online"
            self.sister_status[sister]["last_contact"] = datetime.now().isoformat()
        
        self.logger.info(f"✅ Scientists Network инициализирован: {len(self.sister_status)} сестёр онлайн")

    def close_network(self) -> None:
        """Закрывает Scientists Network."""
        self._save_interaction_log()
        self.logger.info("📡 Scientists Network закрыт")

    # ================================================================
    #  ОБМЕН ДАННЫМИ
    # ================================================================

    def send_request(self, to_sister: str, task_type: str, description: str, 
                     priority: str = "medium", context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Отправляет запрос сестре.
        
        Args:
            to_sister: Имя сестры
            task_type: Тип задачи
            description: Описание задачи
            priority: Приоритет
            context: Дополнительный контекст
            
        Returns:
            Результат отправки
        """
        if to_sister not in self.sister_status:
            self.logger.warning(f"⚠️ Неизвестная сестра: {to_sister}")
            return {"status": "error", "message": f"Неизвестная сестра: {to_sister}"}
        
        self.logger.info(f"📤 Запрос отправлен {to_sister}: {task_type} — {description[:50]}...")
        
        request = {
            "request_id": f"REQ-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "from": "Наото",
            "to": to_sister,
            "task_type": task_type,
            "description": description,
            "priority": priority,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Обновление статуса
        self.sister_status[to_sister]["requests_sent"] += 1
        self.sister_status[to_sister]["last_contact"] = datetime.now().isoformat()
        
        # Запись в журнал
        self._log_interaction("request_sent", request)
        
        return {
            "status": "sent",
            "request_id": request["request_id"],
            "to": to_sister,
            "timestamp": request["timestamp"]
        }

    def receive_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Принимает запрос от сестры.
        
        Args:
            request: Запрос в формате AI Communication Protocol
            
        Returns:
            Подтверждение приёма
        """
        from_sister = request.get("from", "unknown")
        task_type = request.get("task_type", "")
        description = request.get("description", "")
        
        self.logger.info(f"📥 Запрос от {from_sister}: {task_type} — {description[:50]}...")
        
        # Обновление статуса
        if from_sister in self.sister_status:
            self.sister_status[from_sister]["requests_received"] += 1
            self.sister_status[from_sister]["last_contact"] = datetime.now().isoformat()
        
        # Запись в журнал
        self._log_interaction("request_received", request)
        
        return {
            "status": "received",
            "request_id": request.get("request_id", ""),
            "from": from_sister,
            "timestamp": datetime.now().isoformat()
        }

    def send_response(self, to_sister: str, request_id: str, result_data: Dict[str, Any],
                      status: str = "completed", notes: str = "") -> Dict[str, Any]:
        """
        Отправляет ответ сестре.
        
        Args:
            to_sister: Имя сестры
            request_id: ID запроса
            result_data: Данные результата
            status: Статус выполнения
            notes: Примечания
            
        Returns:
            Результат отправки
        """
        if to_sister not in self.sister_status:
            self.logger.warning(f"⚠️ Неизвестная сестра: {to_sister}")
            return {"status": "error", "message": f"Неизвестная сестра: {to_sister}"}
        
        self.logger.info(f"📤 Ответ для {to_sister}: {status} — {request_id}")
        
        response = {
            "response_id": f"RES-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "to": to_sister,
            "from": "Наото",
            "request_id": request_id,
            "status": status,
            "result": result_data,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        # Обновление статуса
        self.sister_status[to_sister]["last_contact"] = datetime.now().isoformat()
        
        # Запись в журнал
        self._log_interaction("response_sent", response)
        
        return {
            "status": "sent",
            "response_id": response["response_id"],
            "to": to_sister,
            "timestamp": response["timestamp"]
        }

    # ================================================================
    #  ОБМЕН ЗНАНИЯМИ
    # ================================================================

    def share_knowledge(self, to_sister: str, knowledge_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Делится знаниями о литературе с сестрой.
        
        Args:
            to_sister: Имя сестры
            knowledge_entry: Запись знаний
            
        Returns:
            Результат обмена
        """
        self.logger.info(f"📚 Обмен знаниями с {to_sister}")
        
        exchange = {
            "exchange_id": f"KNW-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "from": "Наото",
            "to": to_sister,
            "type": "knowledge_share",
            "knowledge": knowledge_entry,
            "timestamp": datetime.now().isoformat()
        }
        
        self._log_interaction("knowledge_shared", exchange)
        
        return {
            "status": "shared",
            "exchange_id": exchange["exchange_id"],
            "to": to_sister
        }

    def request_knowledge(self, from_sister: str, topic: str) -> Dict[str, Any]:
        """
        Запрашивает знания у сестры.
        
        Args:
            from_sister: Имя сестры
            topic: Тема знаний
            
        Returns:
            Результат запроса
        """
        self.logger.info(f"📚 Запрос знаний у {from_sister}: {topic}")
        
        # Генерация "ответа" (в реальности — ожидание ответа от сестры)
        response = {
            "status": "pending",
            "topic": topic,
            "from": from_sister,
            "message": f"Запрос на тему '{topic}' отправлен {from_sister}"
        }
        
        self._log_interaction("knowledge_requested", response)
        
        return response

    # ================================================================
    #  МОНИТОРИНГ СОСТОЯНИЯ СЁСТЕР
    # ================================================================

    def monitor_all_sisters(self) -> Dict[str, Any]:
        """
        Мониторит состояние всех сестёр через Scientists Network.
        
        Returns:
            Полный отчёт о состоянии всех сестёр
        """
        self.logger.info("📊 Запуск мониторинга состояния всех сестёр")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_sisters": len(self.sister_status),
            "active_sisters": 0,
            "inactive_sisters": 0,
            "sisters": {}
        }
        
        for sister_name, status in self.sister_status.items():
            sister_report = {
                "status": status.get("status", "unknown"),
                "last_contact": status.get("last_contact"),
                "requests_sent": status.get("requests_sent", 0),
                "requests_received": status.get("requests_received", 0),
                "specialization": self._get_specialization(sister_name)
            }
            
            report["sisters"][sister_name] = sister_report
            
            if status.get("status") == "online":
                report["active_sisters"] += 1
            else:
                report["inactive_sisters"] += 1
        
        self.logger.info(
            f"📊 Мониторинг завершён: {report['active_sisters']} активных, "
            f"{report['inactive_sisters']} неактивных"
        )
        
        return report

    def _get_specialization(self, sister_name: str) -> str:
        """Возвращает специализацию сестры."""
        specializations = {
            "Футаба": "Система управления и развитие",
            "Фуюки": "Электричество и электромагнетизм",
            "Люси": "Инженерия, проектирование двигателей",
            "Ханако": "Гравитация и гравитационные теории",
            "Шиори": "Иммунная система защиты",
            "Нобука": "Код, тестирование, улучшения",
            "Аква": "Математика, физика, аэродинамика",
            "Селеста": "Биология, физиология, анатомия",
            "Latislane": "Проектирование тел (механических, бионических, органических)",
            "Юи": "Сознание, перенос разума, оцифровка души"
        }
        return specializations.get(sister_name, "Неизвестная специализация")

    def request_visual_work(self, from_sister: str, task_type: str, 
                           description: str, priority: str = "medium") -> Dict[str, Any]:
        """
        Обработка запроса литературного анализа от сестры.
        
        Args:
            from_sister: Имя сестры
            task_type: Тип анализа
            description: Описание
            priority: Приоритет
            
        Returns:
            Результат обработки
        """
        self.logger.info(f"📖 Запрос литературного анализа от {from_sister}: {task_type}")
        
        # Обновление статуса сестры
        if from_sister in self.sister_status:
            self.sister_status[from_sister]["status"] = "online"
            self.sister_status[from_sister]["last_contact"] = datetime.now().isoformat()
        
        # Запись в журнал
        self._log_interaction("literary_request", {
            "from": from_sister,
            "task_type": task_type,
            "description": description,
            "priority": priority
        })
        
        return {
            "status": "received",
            "from": from_sister,
            "task_type": task_type,
            "message": f"Запрос на {task_type} от {from_sister} принят"
        }

    # ================================================================
    #  ЖУРНАЛ ВЗАИМОДЕЙСТВИЙ
    # ================================================================

    def _log_interaction(self, interaction_type: str, data: Dict[str, Any]) -> None:
        """Записывает взаимодействие в журнал."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "data": data
        }
        
        self.interaction_log.append(entry)
        
        # Ограничение размера
        if len(self.interaction_log) > 1000:
            self.interaction_log = self.interaction_log[-500:]
        
        # Автосохранение
        self._save_interaction_log()

    def count(self) -> int:
        """Возвращает количество записей в журнале."""
        return len(self.interaction_log)

    def get_sister_status(self, sister_name: str) -> Optional[Dict[str, Any]]:
        """Возвращает статус сестры."""
        return self.sister_status.get(sister_name)

    def get_all_sister_status(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает статусы всех сестёр."""
        return self.sister_status

    # ================================================================
    #  СОХРАНЕНИЕ И ЗАГРУЗКА
    # ================================================================

    def _save_interaction_log(self) -> None:
        """Сохраняет журнал взаимодействий."""
        try:
            log_file = Path(self.config.state_dir) / "interaction_log.json"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump({
                    "interactions": self.interaction_log[-500:],
                    "sister_status": self.sister_status,
                    "updated": datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            self.logger.debug("💾 Журнал взаимодействий сохранён")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения журнала: {e}")

    def _load_interaction_log(self) -> None:
        """Загружает журнал взаимодействий."""
        log_file = Path(self.config.state_dir) / "interaction_log.json"
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.interaction_log = data.get("interactions", [])
                    loaded_status = data.get("sister_status", {})
                    for sister in loaded_status:
                        if sister in self.sister_status:
                            self.sister_status[sister] = loaded_status[sister]
                    self.logger.info(f"📂 Журнал загружен: {len(self.interaction_log)} записей")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки журнала: {e}")
