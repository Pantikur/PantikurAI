"""
Наото — Визуальный Архитектор Нейросети Вугларст.

Полный цикл визуального представления: набросок → чертёж → 3D-модель.
Модули: мониторинг, самообучение, интернет, автономность, общение.
"""

from __future__ import annotations

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


from naoto.engine.config import NaotoConfig
from naoto.engine.models import VisualTask, VisualResult
from naoto.engine.naoto_core import NaotoCore
from naoto.engine.web_access import NaotoWebAccess
from naoto.engine.monitoring import NaotoMonitoring
from naoto.engine.self_learning import NaotoSelfLearning
from naoto.engine.communication import NaotoCommunication


class Naoto:
    """
    Главный класс Наото — Визуальный Архитектор.
    
    Интегрирует все модули:
    - Мониторинг графических трендов
    - Самообучение и анализ работ
    - Доступ в интернет (референсы, обучение)
    - Автономное выполнение задач
    - Общение с другими AI-агентами
    """

    def __init__(self, config: Optional[NaotoConfig] = None):
        self.config = config or NaotoConfig()
        self.logger = logging.getLogger("Naoto")
        
        # Инициализация модулей
        self.core = NaotoCore(self.config)
        self.web = NaotoWebAccess(self.config)
        self.monitoring = NaotoMonitoring(self.config, self.web)
        self.self_learning = NaotoSelfLearning(self.config)
        self.communication = NaotoCommunication(self.config)
        
        # Загрузка состояния
        self._load_state()
        
        self.logger.info("🎨 Наото инициализирована как Визуальный Архитектор")

    # ================================================================
    #  ЖИЗНЕННЫЙ ЦИКЛ
    # ================================================================

    def start(self) -> None:
        """Запуск всех модулей Наото."""
        self.logger.info("🚀 Запуск Наото — Визуальный Архитектор")
        
        # Загрузка базы знаний
        self.core.load_knowledge()
        
        # Запуск мониторинга
        self.monitoring.start_monitoring()
        
        # Инициализация коммуникации
        self.communication.init_network()
        
        self.logger.info("✅ Наото готова к работе")

    def stop(self) -> None:
        """Остановка всех модулей."""
        self.logger.info("🛑 Остановка Наото")
        
        self.monitoring.stop_monitoring()
        self.communication.close_network()
        self._save_state()
        
        self.logger.info("✅ Наото остановлена")

    # ================================================================
    #  ОСНОВНЫЕ ДЕЙСТВИЯ
    # ================================================================

    def create_sketch(self, description: str, style: str = "freehand") -> Optional[VisualResult]:
        """
        Создать набросок по описанию.
        
        Args:
            description: Описание того, что нужно нарисовать
            style: Стиль (freehand, technical, concept)
            
        Returns:
            Результат с параметрами наброска
        """
        self.logger.info(f"🎨 Создание наброска: {description[:50]}... (стиль: {style})")
        
        # Поиск референсов
        references = self.web.search_references(description, max_results=5)
        
        # Создание наброска
        result = self.core.create_sketch(description, style, references)
        
        # Самооценка
        quality = self.core.evaluate_quality(result, "sketch")
        result.quality_score = quality
        
        # Запись в журнал
        self.core.log_action("sketch", result)
        
        # Сохранение в базу знаний
        self.self_learning.record_creation(result, "sketch")
        
        return result

    def create_drawing(self, description: str, standards: str = "iso") -> Optional[VisualResult]:
        """
        Создать технический чертёж.
        
        Args:
            description: Описание объекта
            standards: Стандарт (iso, gost, ansi)
            
        Returns:
            Результат с параметрами чертежа
        """
        self.logger.info(f"📐 Создание чертежа: {description[:50]}... (стандарт: {standards})")
        
        # Поиск референсов и чертежей
        references = self.web.search_technical_references(description, max_results=3)
        
        # Создание чертежа
        result = self.core.create_drawing(description, standards, references)
        
        # Проверка точности
        accuracy = self.core.check_drawing_accuracy(result)
        result.accuracy = accuracy
        
        # Запись в журнал
        self.core.log_action("drawing", result)
        
        return result

    def create_3d_model(self, description: str, detail_level: str = "mid") -> Optional[VisualResult]:
        """
        Создать 3D-модель.
        
        Args:
            description: Описание объекта
            detail_level: Уровень детализации (low, mid, high)
            
        Returns:
            Результат с параметрами 3D-модели
        """
        self.logger.info(f"🧊 Создание 3D-модели: {description[:50]}... (детализация: {detail_level})")
        
        # Поиск референсов
        references = self.web.search_3d_references(description, max_results=5)
        
        # Создание модели
        result = self.core.create_3d_model(description, detail_level, references)
        
        # Самооценка
        quality = self.core.evaluate_quality(result, "3d")
        result.quality_score = quality
        
        # Запись в журнал
        self.core.log_action("3d", result)
        
        # Запись в базу знаний
        self.self_learning.record_creation(result, "3d")
        
        return result

    # ================================================================
    #  МОНИТОРИНГ
    # ================================================================

    def run_monitoring_cycle(self) -> List[Dict[str, Any]]:
        """Запустить цикл мониторинга графических трендов."""
        self.logger.info("📊 Запуск цикла мониторинга")
        
        trends = self.monitoring.run_cycle()
        
        # Интеграция новых трендов в базу знаний
        for trend in trends:
            if trend.get("relevance") == "high":
                self.self_learning.add_trend_to_knowledge(trend)
        
        return trends

    # ================================================================
    #  САМООБУЧЕНИЕ
    # ================================================================

    def analyze_reference(self, url: str, category: str = "general") -> Dict[str, Any]:
        """
        Проанализировать референс и извлечь техники.
        
        Args:
            url: URL референса
            category: Категория (perspective, lighting, anatomy, texture, composition)
            
        Returns:
            Извлечённые техники и знания
        """
        self.logger.info(f"📚 Анализ референса: {url[:50]}... (категория: {category})")
        
        # Загрузка контента
        content = self.web.fetch_web_content(url)
        
        if not content:
            self.logger.error(f"❌ Не удалось загрузить референс: {url}")
            return {"error": "Не удалось загрузить"}
        
        # Анализ
        analysis = self.self_learning.analyze_content(content, category, url)
        
        # Запись в базу знаний
        self.self_learning.record_learning(analysis)
        
        return analysis

    def learn_new_technique(self, technique_name: str, description: str) -> bool:
        """
        Записать новую технику в базу знаний.
        
        Args:
            technique_name: Название техники
            description: Описание техники
            
        Returns:
            True если запись успешна
        """
        self.logger.info(f"📖 Изучение новой техники: {technique_name}")
        
        return self.self_learning.add_technique(technique_name, description)

    # ================================================================
    #  КОММУНИКАЦИЯ
    # ================================================================

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработать запрос от другого AI-агента.
        
        Args:
            request: Запрос в формате AI Communication Protocol
            
        Returns:
            Ответ в формате AI Communication Protocol
        """
        self.logger.info(f"📡 Получен запрос от {request.get('from', 'unknown')}")
        
        task_type = request.get("task_type", "")
        description = request.get("description", "")
        priority = request.get("priority", "medium")
        
        # Выполнение визуальной задачи
        result = self._execute_visual_task(task_type, description, priority)
        
        # Формирование ответа
        response = {
            "response_id": f"RES-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}",
            "to": request.get("from", "unknown"),
            "request_id": request.get("request_id", ""),
            "status": result.get("status", "completed"),
            "result": result.get("result", {}),
            "notes": result.get("notes", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        # Запись в журнал
        self.core.log_action("communication", {"response": response})
        
        return response

    def _execute_visual_task(self, task_type: str, description: str, priority: str) -> Dict[str, Any]:
        """Выполнить визуальную задачу."""
        
        if task_type == "sketch":
            sketch = self.create_sketch(description)
            if sketch:
                return {
                    "status": "completed",
                    "result": {
                        "type": "sketch",
                        "data": sketch.to_dict(),
                        "description": f"Набросок: {description}"
                    },
                    "notes": f"Качество: {sketch.quality_score:.2f}"
                }
        
        elif task_type == "drawing":
            drawing = self.create_drawing(description)
            if drawing:
                return {
                    "status": "completed",
                    "result": {
                        "type": "drawing",
                        "data": drawing.to_dict(),
                        "description": f"Чертёж: {description}"
                    },
                    "notes": f"Точность: {drawing.accuracy:.2f}"
                }
        
        elif task_type == "3d":
            model = self.create_3d_model(description)
            if model:
                return {
                    "status": "completed",
                    "result": {
                        "type": "3d",
                        "data": model.to_dict(),
                        "description": f"3D-модель: {description}"
                    },
                    "notes": f"Качество: {model.quality_score:.2f}"
                }
        
        elif task_type == "reference":
            references = self.web.search_references(description, max_results=5)
            return {
                "status": "completed",
                "result": {
                    "type": "reference",
                    "data": references,
                    "description": f"Референсы: {description}"
                },
                "notes": f"Найдено: {len(references)}"
            }
        
        else:
            return {
                "status": "rejected",
                "result": {},
                "notes": f"Неизвестный тип задачи: {task_type}"
            }
        
        return {
            "status": "partial",
            "result": {},
            "notes": "Ошибка выполнения задачи"
        }

    # ================================================================
    #  АВТОНОМНОСТЬ
    # ================================================================

    def autonomous_task(self, description: str, autonomy_level: str = "full") -> Dict[str, Any]:
        """
        Выполнить задачу автономно.
        
        Args:
            description: Описание задачи
            autonomy_level: Уровень автономности (full, partial, minimal)
            
        Returns:
            Результат выполнения
        """
        self.logger.info(f"🤖 Автономная задача: {description[:50]}... (уровень: {autonomy_level})")
        
        # Анализ задачи
        analysis = self.core.analyze_task(description)
        
        # Выбор типа визуализации
        task_type = analysis.get("task_type", "sketch")
        
        # Поиск референсов
        references = self.web.search_references(description, max_results=5)
        
        # Выполнение
        if task_type == "sketch":
            result = self.create_sketch(description)
        elif task_type == "drawing":
            result = self.create_drawing(description)
        elif task_type == "3d":
            result = self.create_3d_model(description)
        else:
            result = self.create_sketch(description)
        
        return {
            "task_description": description,
            "task_type": task_type,
            "references_found": len(references),
            "result": result.to_dict() if result else None,
            "autonomy_level": autonomy_level,
            "timestamp": datetime.now().isoformat()
        }

    # ================================================================
    #  СОСТОЯНИЕ
    # ================================================================

    def _load_state(self) -> None:
        """Загружает состояние из файла."""
        state_file = Path("naoto/engine/state/state.json")
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    self.logger.info(f"📂 Состояние загружено: {state.get('version', 'unknown')}")
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки состояния: {e}")

    def _save_state(self) -> None:
        """Сохраняет состояние в файл."""
        state_file = Path("naoto/engine/state/state.json")
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "knowledge_count": self.core.knowledge_count(),
            "actions_count": self.core.actions_count(),
            "communication_count": self.communication.count()
        }
        
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            self.logger.debug("💾 Состояние сохранено")
        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения состояния: {e}")
