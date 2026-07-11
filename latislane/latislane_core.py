"""
Latislane — Основное ядро системы.

Объединяет:
- Модули тела
- Интернет-обучение
- Фабрику тел
- Автономное управление
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .body_modules import (
    BodyModule,
    BodyType,
    BodySpecification,
    create_default_modules
)
from .internet_learning import InternetLearningEngine
from .body_factory import BodyFactory
from .evolution_manager import EvolutionManager

logger = logging.getLogger("latislane.core")


class LatislaneCore:
    """
    Основное ядро системы Латислейн.
    
    Это 'мозг' системы, который:
    1. Управляет изучением тела человека
    2. Координирует проектирование тел
    3. Контролирует процесс самообучения
    4. Интегрируется с чат-ботом Pantikur
    """
    
    def __init__(self, project_root: str = ".", demo_mode: bool = True):
        self.project_root = Path(project_root)
        self.demo_mode = demo_mode
        
        # === Автономность ===
        self.max_autonomy_level = "L3"        # L0-L4
        self.autonomy_level = "L0"            # текущий уровень
        self.require_confirmation_above = "L2"  # выше этого уровня — запрос подтверждения
        
        # Директория данных
        self.data_dir = self.project_root / "data" / "latislane"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализация подсистем
        self.learning_engine = InternetLearningEngine(
            data_dir=str(self.data_dir / "learning")
        )
        
        # Создание модулей тела
        self.body_modules = create_default_modules()
        
        # Фабрика тел
        self.body_factory = BodyFactory(
            body_modules=self.body_modules,
            learning_engine=self.learning_engine,
            data_dir=str(self.data_dir / "bodies")
        )
        
        # Менеджер эволюции
        self.evolution = EvolutionManager(
            data_dir=str(self.data_dir / "evolution")
        )
        
        # Состояние системы
        self.system_state = {
            "initialized_at": time.time(),
            "total_bodies_designed": 0,
            "total_research_cycles": 0,
            "total_evolution_transitions": 0,
            "current_focus": "anatomy_study",  # "anatomy_study", "mechanical_design", "bionic_design", "organic_design"
            "integration_status": {
                "chatbot": False,
                "internet_learning": True,
                "body_factory": True
            }
        }
        
        # Журнал событий
        self.event_log: List[Dict[str, Any]] = []
        
        # Загрузка состояния
        self._load_state()
        
        logger.info("🧬 LatislaneCore инициализирован")
        logger.info(f"   📚 Модулей тела: {len(self.body_modules)}")
        logger.info(f"   🔍 Движок обучения активен")
        logger.info(f"   🏭 Фабрика тел готова")
        logger.info(f"   🌐 Демо-режим: {'ВКЛ' if demo_mode else 'ВЫКЛ'}")
    
    def _load_state(self):
        """Загрузить состояние системы."""
        state_file = self.data_dir / "system_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self.system_state.update(state.get("system_state", {}))
                self.event_log = state.get("event_log", [])[-100:]
                logger.info(f"✅ Состояние системы загружено")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки состояния: {e}")
        else:
            logger.info("ℹ️ Новое состояние системы создано")
    
    def _save_state(self):
        """Сохранить состояние системы."""
        state = {
            "system_state": self.system_state,
            "event_log": self.event_log[-100:],
            "saved_at": time.time()
        }
        
        state_file = self.data_dir / "system_state.json"
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения состояния: {e}")
    
    def log_event(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """Записать событие в журнал."""
        event = {
            "type": event_type,
            "message": message,
            "data": data or {},
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat()
        }
        self.event_log.append(event)
        logger.info(f"[{event_type}] {message}")
    
    def start_anatomy_study(self):
        """Начать изучение анатомии человека."""
        logger.info("📖 Запуск изучения анатомии человека")
        self.system_state["current_focus"] = "anatomy_study"
        self.log_event("STUDY_STARTED", "Изучение анатомии начато")
        
        # Определение пробелов в знаниях
        gaps = self.learning_engine.get_knowledge_gaps()
        
        if gaps:
            logger.info(f"🎯 Определено {len(gaps)} тем для изучения")
            self.log_event("GAPS_IDENTIFIED", f"Определено {len(gaps)} пробелов", {"topics": gaps[:5]})
        else:
            logger.info("✅ Все темы уже изучены")
            self.log_event("ALL_STUDIED", "Все темы анатомии изучены")
        
        self._save_state()
    
    async def run_study_cycle(self, topics: Optional[List[str]] = None, batch_size: int = 3):
        """
        Запустить цикл обучения.
        
        :param topics: Список тем (если None, определяются автоматически)
        :param batch_size: Размер пакета
        """
        logger.info("🔄 Запуск цикла обучения")
        self.system_state["total_research_cycles"] += 1
        
        # Определение тем
        if topics is None:
            topics = self.learning_engine.get_knowledge_gaps()[:10]
        
        if not topics:
            logger.info("ℹ️ Нет тем для изучения")
            return
        
        # Обучение
        results = await self.learning_engine.learn_batch(topics, batch_size)
        
        logger.info(f"✅ Цикл завершён: {results['completed']}/{results['total_topics']} тем")
        self.log_event("STUDY_CYCLE_COMPLETED", "Цикл обучения завершён", results)
        
        # Проверка эволюции
        self._check_evolution()
        
        self._save_state()
    
    def _check_evolution(self):
        """Проверить, можно ли продвинуться в эволюции."""
        learned_topics = len(self.learning_engine.topic_progress)
        
        if self.evolution.can_advance(learned_topics):
            logger.info(f"🎉 Эволюция: можно перейти к следующему этапу!")
            self.evolution.advance(reason="topics_learned")
            self.system_state["total_evolution_transitions"] += 1
    
    def design_mechanical_body(self, name: str = "Mechanical-01") -> BodySpecification:
        """
        Спроектировать механическое тело.
        
        :param name: Имя проекта
        :return: Спецификация тела
        """
        logger.info(f"🤖 Проектирование механического тела: {name}")
        
        self.system_state["current_focus"] = "mechanical_design"
        self.log_event("DESIGN_STARTED", f"Проектирование механического тела: {name}")
        
        # Создание спецификации
        spec = self.body_factory.create_body_specification(
            name=name,
            body_type=BodyType.MECHANICAL
        )
        
        # Проектирование модулей
        spec = self.body_factory.design_modules_for_body_type(spec, BodyType.MECHANICAL)
        
        logger.info(f"✅ Механическое тело спроектировано: {name}")
        self.system_state["total_bodies_designed"] += 1
        self.log_event("DESIGN_COMPLETED", f"Механическое тело завершено: {name}", spec.get_stats())
        
        self._save_state()
        return spec
    
    def design_bionic_body(self, name: str = "Bionic-01") -> BodySpecification:
        """
        Спроектировать бионическое тело.
        
        :param name: Имя проекта
        :return: Спецификация тела
        """
        logger.info(f"🦾 Проектирование бионического тела: {name}")
        
        self.system_state["current_focus"] = "bionic_design"
        self.log_event("DESIGN_STARTED", f"Проектирование бионического тела: {name}")
        
        # Создание спецификации
        spec = self.body_factory.create_body_specification(
            name=name,
            body_type=BodyType.BIONIC
        )
        
        # Проектирование модулей
        spec = self.body_factory.design_modules_for_body_type(spec, BodyType.BIONIC)
        
        logger.info(f"✅ Бионическое тело спроектировано: {name}")
        self.system_state["total_bodies_designed"] += 1
        self.log_event("DESIGN_COMPLETED", f"Бионическое тело завершено: {name}", spec.get_stats())
        
        self._save_state()
        return spec
    
    def design_organic_body(self, name: str = "Organic-01") -> BodySpecification:
        """
        Спроектировать органическое тело.
        
        :param name: Имя проекта
        :return: Спецификация тела
        """
        logger.info(f"🧬 Проектирование органического тела: {name}")
        
        self.system_state["current_focus"] = "organic_design"
        self.log_event("DESIGN_STARTED", f"Проектирование органического тела: {name}")
        
        # Создание спецификации
        spec = self.body_factory.create_body_specification(
            name=name,
            body_type=BodyType.ORGANIC
        )
        
        # Проектирование модулей
        spec = self.body_factory.design_modules_for_body_type(spec, BodyType.ORGANIC)
        
        logger.info(f"✅ Органическое тело спроектировано: {name}")
        self.system_state["total_bodies_designed"] += 1
        self.log_event("DESIGN_COMPLETED", f"Органическое тело завершено: {name}", spec.get_stats())
        
        self._save_state()
        return spec
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить статус всей системы."""
        return {
            "system_state": self.system_state,
            "modules_count": len(self.body_modules),
            "learning_report": self.learning_engine.get_learning_report(),
            "factory_status": self.body_factory.get_status(),
            "event_log_count": len(self.event_log),
            "last_events": self.event_log[-10:]
        }
    
    def get_anatomy_report(self) -> Dict[str, Any]:
        """Получить отчёт по изученной анатомии."""
        report = {
            "modules": {},
            "overall_progress": 0.0
        }
        
        total_progress = 0.0
        
        for name, module in self.body_modules.items():
            report["modules"][name] = module.to_dict()
            total_progress += module.research_progress
        
        report["overall_progress"] = total_progress / len(self.body_modules) if self.body_modules else 0
        
        return report
    
    def integrate_with_chatbot(self, chatbot_instance: Any = None):
        """
        Интеграция с чат-ботом Pantikur.
        
        Позволяет боту:
        - Запрашивать знания анатомии
        - Получать спецификации тел
        - Запускать изучение тем
        """
        logger.info("🔗 Интеграция с чат-ботом Pantikur")
        
        self.system_state["integration_status"]["chatbot"] = True
        self.system_state["chatbot_version"] = "1.5.0"
        
        self.log_event("INTEGRATION", "Интеграция с чат-ботом завершена")
        self._save_state()
        
        logger.info("✅ Интеграция завершена")
    
    def start_autonomous_learning(self, interval_minutes: int = 10):
        """
        Запустить автономное обучение.
        
        :param interval_minutes: Интервал между циклами (минуты)
        """
        logger.info(f"🚀 Запуск автономного обучения (интервал: {interval_minutes} мин)")
        
        self.system_state["current_focus"] = "autonomous_learning"
        self.log_event("AUTO_LEARNING_STARTED", f"Автономное обучение запущено, интервал: {interval_minutes} мин")
        
        # Запуск в фоне
        import asyncio
        
        async def _run():
            await self.learning_engine.run_continuous_learning(interval_minutes)
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_run())
            else:
                loop.run_until_complete(_run())
        except Exception as e:
            logger.error(f"❌ Ошибка запуска автономного обучения: {e}")
        
        self._save_state()
    
    async def self_improve(self):
        """
        Саморазвитие: анализ слабых мест и улучшение знаний.
        
        1. Анализирует пробелы в знаниях
        2. Ищет новые темы для изучения
        3. Обновляет старые знания
        4. Пересматривает низкую уверенность
        """
        logger.info("🔄 Запуск саморазвития...")
        
        # 1. Анализ пробелов
        gaps = self.learning_engine.get_knowledge_gaps()
        
        if gaps:
            # 2. Изучение новых тем
            logger.info(f"📚 Изучение {len(gaps)} новых тем...")
            await self.run_study_cycle(topics=gaps[:5], batch_size=3)
        
        # 3. Обновление низкой уверенности
        low_confidence_nodes = [
            node for node in self.learning_engine.knowledge_nodes.values()
            if node.confidence < 0.5
        ]
        
        if low_confidence_nodes:
            logger.info(f"🔄 Обновление {len(low_confidence_nodes)} узлов с низкой уверенностью...")
            for node in low_confidence_nodes[:5]:
                # Перепроверка через веб-поиск
                research = await self.learning_engine.web_researcher.learn_from_search(node.topic) if self.learning_engine.web_researcher else None
                if research and research.get("facts"):
                    node.confidence = min(1.0, node.confidence + 0.2)
                    node.is_verified = True
        
        # 4. Сохранение
        self._save_state()
        logger.info("✅ Саморазвитие завершено")
    
    def export_all(self, output_dir: Optional[str] = None) -> str:
        """Экспорт всех данных системы."""
        if output_dir is None:
            output_dir = str(self.data_dir / "exports")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Экспорт знаний
        knowledge_file = self.learning_engine.export_knowledge(
            str(output_path / "knowledge.json")
        )
        
        # Экспорт спецификаций
        specs = self.body_factory.export_all_specs(str(output_path / "bodies"))
        
        # Экспорт состояния системы
        state_file = output_path / "system_state_export.json"
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump({
                "exported_at": time.time(),
                "system": self.system_state,
                "modules": {name: mod.to_dict() for name, mod in self.body_modules.items()},
                "event_log": self.event_log[-100:]
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📤 Весь экспорт завершён: {output_path}")
        return str(output_path)
    
    def chat_response(self, user_message: str) -> str:
        """
        Ответ на вопрос через Латислейн.
        
        Используется для интеграции с чат-ботом.
        """
        msg_lower = user_message.lower()
        
        # Определение намерения
        if any(kw in msg_lower for kw in ["эволюция", "этап", "прогресс эволю", "стадия"]):
            return self.evolution.chat_response(user_message)
        
        elif any(kw in msg_lower for kw in ["анатомия", "тело", "органы", "строение"]):
            report = self.get_anatomy_report()
            progress = report["overall_progress"] * 100
            return (
                f"🧬 **Латислейн: Статус изучения тела**\n\n"
                f"Изучено модулей: {len(report['modules'])}\n"
                f"Общий прогресс: {progress:.1f}%\n\n"
                f"Ключевые модули:\n"
            ) + "\n".join(
                f"- {name}: {mod['research_progress']*100:.0f}%"
                for name, mod in list(report["modules"].items())[:5]
            )
        
        elif any(kw in msg_lower for kw in ["механич", "робот", "протез"]):
            return (
                "🤖 **Латислейн: Механические тела**\n\n"
                "Механические тела проектируются на основе:\n"
                "- Скелет: титановые сплавы, алюминиевые конструкции\n"
                "- Мышцы: электроактивные полимеры, соленоиды\n"
                "- Нервная система: нейроморфные чипы, BCI\n"
                "- Энергия: литий-полимерные батареи, топливные элементы\n\n"
                f"Проектировано тел: {self.system_state['total_bodies_designed']}"
            )
        
        elif any(kw in msg_lower for kw in ["бионик", "имплант", "гибрид"]):
            return (
                "🦾 **Латислейн: Бионические тела**\n\n"
                "Бионические тела комбинируют:\n"
                "- Органические ткани + искусственные компоненты\n"
                "- Нейроинтерфейсы для контроля\n"
                "- Тактильные сенсоры обратной связи\n"
                "- Биосовместимые импланты\n\n"
                "Стадии: исследование → дизайн → прототип → тестирование"
            )
        
        elif any(kw in msg_lower for kw in ["органич", "генн", "биоинженер", "вырастить"]):
            return (
                "🧬 **Латислейн: Органические тела**\n\n"
                "Органические тела создаются через:\n"
                "- Генную инженерию (CRISPR-Cas9)\n"
                "- Тканевую инженерию (степ-клетки)\n"
                "- 3D биопечать органов\n"
                "- Клонирование (репродуктивное)\n\n"
                f"Прогресс изучения анатомии: {self.get_anatomy_report()['overall_progress']*100:.1f}%"
            )
        
        elif any(kw in msg_lower for kw in ["статус", "прогресс", "как дела"]):
            status = self.get_system_status()
            return (
                f"📊 **Латислейн: Системный статус**\n\n"
                f"Фокус: {status['system_state']['current_focus']}\n"
                f"Циклов обучения: {status['system_state']['total_research_cycles']}\n"
                f"Тел спроектировано: {status['system_state']['total_bodies_designed']}\n"
                f"Узлов знаний: {status['learning_report']['knowledge_nodes']}\n"
                f"Прогресс обучения: {status['learning_report']['overall_progress']*100:.1f}%"
            )
        
        else:
            return (
                "🧬 **Латислейн активен**\n\n"
                "Я изучаю тело человека для проектирования новых тел.\n\n"
                "Запросы:\n"
                "- 'анатомия' — статус изучения\n"
                "- 'механическое тело' — информация о робототехнике\n"
                "- 'бионическое тело' — информация о гибридах\n"
                "- 'органическое тело' — биоинженерия\n"
                "- 'статус' — системный статус"
            )
