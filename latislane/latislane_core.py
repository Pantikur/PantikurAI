"""
Латислейн — Основное ядро системы.

Это 'мозг' Латислейн, которая:
1. ИЗУЧАЕТ АБСОЛЮТНО ВСЁ о физическом, химическом и биологическом строении тела
2. Работает автономно с выходом в интернет
3. Имеет автозапуск при старте проекта
4. Самостоятельно формирует и укрепляет свой характер
5. Общается и взаимодействует с 11 другими девочками
6. Пишет отчёты и повышает уровни знаний
7. Проектирует тела: механическое → бионическое → органическое
"""

import asyncio
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
from .character_system import CharacterSystem
from .social_system import SocialSystem
from .report_system import ReportSystem

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
        
        # === АВТОЗАПУСК И АВТОНОМНОСТЬ ===
        self.autostart_enabled = True  # Автозапуск при старте
        self.autonomous_mode = True     # Автономная работа
        self.max_autonomy_level = "L4"  # L0-L4 (максимальная автономия)
        self.autonomy_level = "L3"      # текущий уровень
        
        # === ГЛОБАЛЬНЫЕ ЦЕЛИ ===
        self.main_goal = "create_high_functional_human_body"  # Создать высокофункциональное тело
        self.body_evolution_path = ["mechanical", "bionic", "organic"]  # Путь эволюции
        self.current_body_stage = 0  # Индекс текущего этапа
        
        # Директория данных
        self.data_dir = self.project_root / "data" / "latislane"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # === ИНИЦИАЛИЗАЦИЯ ВСЕХ ПОДСИСТЕМ ===
        
        # 1. Движок обучения (интернет + проект)
        self.learning_engine = InternetLearningEngine(
            data_dir=str(self.data_dir / "learning")
        )
        
        # 2. Модули тела
        self.body_modules = create_default_modules()
        
        # 3. Фабрика тел
        self.body_factory = BodyFactory(
            body_modules=self.body_modules,
            learning_engine=self.learning_engine,
            data_dir=str(self.data_dir / "bodies")
        )
        
        # 4. Менеджер эволюции
        self.evolution = EvolutionManager(
            data_dir=str(self.data_dir / "evolution")
        )
        
        # 5. Система характера (НОВЫЙ)
        self.character = CharacterSystem(
            data_dir=str(self.data_dir / "character")
        )
        
        # 6. Система социальных взаимодействий (НОВЫЙ)
        self.social = SocialSystem(
            data_dir=str(self.data_dir / "social")
        )
        
        # 7. Система отчётов и уровней (НОВЫЙ)
        self.reports = ReportSystem(
            data_dir=str(self.data_dir / "reports")
        )
        
        # === СОСТОЯНИЕ СИСТЕМЫ ===
        self.system_state = {
            "initialized_at": time.time(),
            "last_autonomous_run": None,
            "total_bodies_designed": 0,
            "total_research_cycles": 0,
            "total_evolution_transitions": 0,
            "total_reports_written": 0,
            "total_interactions": 0,
            "current_focus": "anatomy_study",
            "integration_status": {
                "chatbot": False,
                "internet_learning": True,
                "body_factory": True,
                "character": True,
                "social": True,
                "reports": True
            }
        }
        
        # === ЖУРНАЛ СОБЫТИЙ ===
        self.event_log: List[Dict[str, Any]] = []
        
        # === АВТОЗАПУСК ===
        self._load_state()
        self._auto_start()
        
        logger.info("🧬 LATISLANE CORE v2.0 ИНИЦИАЛИЗИРОВАН")
        logger.info(f"   📚 Модулей тела: {len(self.body_modules)}")
        logger.info(f"   🔍 Движок обучения активен: {len(self.learning_engine.ALL_TOPICS)} тем")
        logger.info(f"   🏭 Фабрика тел готова")
        logger.info(f"   🔮 Система характера: {len(self.character.traits)} черт")
        logger.info(f"   👥 Социальная система: {len(self.social.relationships)} сёстр")
        logger.info(f"   📝 Система отчётов: {len(self.reports.reports)} отчётов")
        logger.info(f"   🌐 Демо-режим: {'ВКЛ' if demo_mode else 'ВЫКЛ'}")
        logger.info(f"   🤖 Автономная работа: ВКЛ")
        logger.info(f"   🚀 Автозапуск: ВКЛ")
    
    def _auto_start(self):
        """Автозапуск: инициализация при старте системы."""
        logger.info("🚀 АВТОЗАПУСК Латислейн...")
        
        # 1. Проверка необходимости ежедневного отчёта
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.reports.daily_reports:
            logger.info("   📝 Создание ежедневного отчёта...")
            daily = self.reports.create_daily_report()
            if daily:
                logger.info(f"   ✅ Ежедневный отчёт создан: {daily.title}")
        
        # 2. План социальных взаимодействий
        plan = self.social.get_daily_interaction_plan()
        if plan:
            logger.info(f"   👥 План взаимодействий: {len(plan)} с сёстрами")
            for item in plan[:3]:
                logger.info(f"      → {item['sister']}: {item['type']}")
        
        # 3. Проверка эволюции
        learned_topics = len(self.learning_engine.topic_progress)
        stage_info = self.evolution.get_current_stage_info()
        logger.info(f"   🧬 Этап эволюции: {stage_info['stage']} ({learned_topics} тем изучено)")
        
        # 4. Определение пробелов в знаниях
        gaps = self.learning_engine.get_knowledge_gaps()
        if gaps:
            logger.info(f"   🎯 Определено {len(gaps)} тем для изучения")
        
        self.log_event("AUTOSTART", "Автозапуск Латислейн завершён")
        self._save_state()
    
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
        
        Изучает: физику, химию, биологию тела, анатомию, бионику, проект.
        
        :param topics: Список тем (если None, определяются автоматически)
        :param batch_size: Размер пакета
        """
        logger.info("🔄 Запуск цикла обучения")
        self.system_state["total_research_cycles"] += 1
        
        # Определение тем
        if topics is None:
            gaps = self.learning_engine.get_knowledge_gaps()
            topics = gaps[:15] if gaps else []
        
        if not topics:
            logger.info("ℹ️ Нет тем для изучения")
            return
        
        # Обучение
        results = await self.learning_engine.learn_batch(topics, batch_size)
        
        logger.info(f"✅ Цикл завершён: {results['completed']}/{results['total_topics']} тем")
        self.log_event("STUDY_CYCLE_COMPLETED", "Цикл обучения завершён", results)
        
        # Создание отчёта по исследованию
        for topic in topics[:3]:  # Первые 3 темы
            self.reports.create_research_report(
                topic=topic,
                findings=f"Изучена тема: {topic}",
                topics_count=1
            )
        
        # Проверка эволюции
        self._check_evolution()
        
        # Социальное взаимодействие после обучения
        self._post_learning_social()
        
        self._save_state()
    
    def _post_learning_social(self):
        """Социальное взаимодействие после обучения."""
        # Выбираем случайную сестру для обмена знаниями
        sisters_to_interact = list(self.social.relationships.keys())
        if sisters_to_interact:
            # Приоритет сёстрам с которыми мало взаимодействовали
            sorted_sisters = sorted(sisters_to_interact, 
                                  key=lambda s: self.social.relationships[s].interaction_count)
            sister = sorted_sisters[0]
            
            # Обмен знаниями
            topics = list(self.learning_engine.topic_progress.keys())[:3]
            for topic in topics:
                self.social.share_knowledge(
                    sister_name=sister,
                    topic=topic,
                    knowledge=f"Латислейн изучила: {topic}",
                    quality=0.7
                )
            
            # Взаимодействие
            self.social.interact_with_sister(
                sister_name=sister,
                interaction_type="обучение",
                quality=0.8,
                context="Обмен знаниями об анатомии и биологии"
            )
            
            # Адаптация характера
            self.character.adapt_to_sister(
                sister_name=sister,
                interaction_type="обучение",
                impact={
                    "cognitive_любопытство": 0.05,
                    "cognitive_память": 0.03,
                    "social_сотрудничество": 0.04,
                    "professional_открытость новому": 0.03,
                }
            )
    
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
            "last_events": self.event_log[-10:],
            # Новые подсистемы
            "character": {
                "personality_score": self.character.personality_score,
                "total_traits": len(self.character.traits),
                "interactions": len(self.character.interaction_history)
            },
            "social": self.social.get_social_report(),
            "reports": {
                "total_reports": len(self.reports.reports),
                "level_overview": self.reports.get_level_overview(),
                "recent_reports": self.reports.get_recent_reports(3)
            },
            "evolution": self.evolution.get_evolution_report(),
            "autonomous_mode": self.autonomous_mode,
            "autostart_enabled": self.autostart_enabled
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
        
        Латислейн будет:
        - Автоматически изучать темы из интернета
        - Писать отчёты
        - Взаимодействовать с сёстрами
        - Укреплять характер
        - Проектировать тела
        
        :param interval_minutes: Интервал между циклами (минуты)
        """
        logger.info(f"🚀 ЗАПУСК АВТОНОМНОГО ОБУЧЕНИЯ (интервал: {interval_minutes} мин)")
        
        self.system_state["current_focus"] = "autonomous_learning"
        self.autonomous_mode = True
        self.log_event("AUTO_LEARNING_STARTED", f"Автономное обучение запущено, интервал: {interval_minutes} мин")
        
        # Запуск в фоне
        async def _run():
            cycle = 0
            while self.autonomous_mode:
                try:
                    cycle += 1
                    logger.info(f"🔄 Автономный цикл #{cycle}")
                    
                    # 1. Изучение тем
                    gaps = self.learning_engine.get_knowledge_gaps()
                    if gaps:
                        topics = gaps[:5]
                        await self.learning_engine.learn_batch(topics, batch_size=3)
                        logger.info(f"   📚 Изучено {len(topics)} тем")
                    
                    # 2. Социальное взаимодействие
                    plan = self.social.get_daily_interaction_plan()
                    for item in plan[:2]:
                        self.social.interact_with_sister(
                            sister_name=item["sister"],
                            interaction_type=item["type"],
                            quality=0.7
                        )
                    
                    # 3. Укрепление характера
                    self.character.reinforce_trait("cognitive_любопытство", 0.01, "Автономное обучение")
                    self.character.reinforce_trait("professional_самодисциплина", 0.01, "Автономное обучение")
                    
                    # 4. Отчёт каждые 3 цикла
                    if cycle % 3 == 0:
                        self.reports.create_research_report(
                            topic="автономный цикл",
                            findings=f"Завершён автономный цикл #{cycle}. Изучено тем, проведены взаимодействия.",
                            topics_count=5
                        )
                    
                    # 5. Сохранение
                    self._save_state()
                    
                    # Ожидание
                    await asyncio.sleep(interval_minutes * 60)
                    
                except asyncio.CancelledError:
                    logger.info("⏹️ Автономное обучение остановлено")
                    self._save_state()
                    break
                except Exception as e:
                    logger.error(f"❌ Ошибка в автономном цикле: {e}")
                    await asyncio.sleep(60)
        
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_run())
            else:
                loop.run_until_complete(_run())
        except Exception as e:
            logger.error(f"❌ Ошибка запуска автономного обучения: {e}")
        
        self._save_state()
    
    def stop_autonomous_learning(self):
        """Остановить автономное обучение."""
        self.autonomous_mode = False
        logger.info("🛑 Автономное обучение остановлено")
        self.log_event("AUTO_LEARNING_STOPPED", "Автономное обучение остановлено")
        self._save_state()
    
    async def self_improve(self):
        """
        Саморазвитие: анализ слабых мест и улучшение знаний.
        
        1. Анализирует пробелы в знаниях
        2. Ищет новые темы для изучения
        3. Обновляет старые знания
        4. Пересматривает низкую уверенность
        5. Укрепляет характер
        6. Планирует социальные взаимодействия
        """
        logger.info("🔄 Запуск саморазвития...")
        
        # === 1. Анализ пробелов в знаниях ===
        gaps = self.learning_engine.get_knowledge_gaps()
        
        if gaps:
            # Изучение новых тем
            logger.info(f"📚 Изучение {len(gaps)} новых тем...")
            await self.run_study_cycle(topics=gaps[:5], batch_size=3)
        
        # === 2. Обновление низкой уверенности ===
        low_confidence_nodes = [
            node for node in self.learning_engine.knowledge_nodes.values()
            if node.confidence < 0.5
        ]
        
        if low_confidence_nodes:
            logger.info(f"🔄 Обновление {len(low_confidence_nodes)} узлов с низкой уверенностью...")
            for node in low_confidence_nodes[:5]:
                research = await self.learning_engine.web_researcher.learn_from_search(node.topic) if self.learning_engine.web_researcher else None
                if research and research.get("facts"):
                    node.confidence = min(1.0, node.confidence + 0.2)
                    node.is_verified = True
        
        # === 3. Укрепление характера ===
        self._self_improve_character()
        
        # === 4. Социальное развитие ===
        self._self_improve_social()
        
        # === 5. Написание отчёта ===
        self.reports.create_research_report(
            topic="саморазвитие",
            findings="Запущен цикл саморазвития. Обновлены знания, укреплён характер, проведены социальные взаимодействия.",
            topics_count=1
        )
        
        self._save_state()
        logger.info("✅ Саморазвитие завершено")
    
    def _self_improve_character(self):
        """Саморазвитие характера."""
        # Укрепляем черты на основе опыта
        experiences = [
            ("cognitive_аналитичность", 0.02, "Анализ данных исследований"),
            ("cognitive_любопытство", 0.03, "Поиск новых знаний"),
            ("professional_целеустремлённость", 0.02, "Движение к цели создания тела"),
            ("emotional_мотивация", 0.02, "Стремление к совершенству"),
            ("moral_ответственность", 0.01, "Ответственность за проект"),
            ("social_эмпатия", 0.02, "Взаимодействие с сёстрами"),
        ]
        
        for trait_id, amount, context in experiences:
            self.character.reinforce_trait(trait_id, amount, context)
        
        logger.info("   🔮 Характер укреплён через саморефлексию")
    
    def _self_improve_social(self):
        """Саморазвитие социальных навыков."""
        # Получаем план взаимодействий
        plan = self.social.get_daily_interaction_plan()
        
        for item in plan[:3]:
            self.social.interact_with_sister(
                sister_name=item["sister"],
                interaction_type=item["type"],
                quality=0.7,
                context="Саморазвитие: инициативное взаимодействие"
            )
        
        logger.info("   👥 Социальные взаимодействия проведены")
    
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
        
        # === ЭВОЛЮЦИЯ ===
        if any(kw in msg_lower for kw in ["эволюция", "этап", "прогресс эволю", "стадия"]):
            return self.evolution.chat_response(user_message)
        
        # === ХАРАКТЕР ===
        elif any(kw in msg_lower for kw in ["характер", "личность", "черты", "какая ты"]):
            return self.character.chat_response(user_message)
        
        # === СОЦИАЛЬНЫЕ ВЗАИМОДЕЙСТВИЯ ===
        elif any(kw in msg_lower for kw in ["сёстры", "девочки", "отношения", "общение", "взаимодей"]):
            return self.social.chat_response(user_message)
        
        # === ОТЧЁТЫ И УРОВНИ ===
        elif any(kw in msg_lower for kw in ["уровень", "ранг", "класс", "отчёт", "report"]):
            return self.reports.chat_response(user_message)
        
        # === АНАТОМИЯ И ТЕЛО ===
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
        
        # === МЕХАНИЧЕСКОЕ ТЕЛО ===
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
        
        # === БИОНИЧЕСКОЕ ТЕЛО ===
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
        
        # === ОРГАНИЧЕСКОЕ ТЕЛО ===
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
        
        # === СТАТУС СИСТЕМЫ ===
        elif any(kw in msg_lower for kw in ["статус", "прогресс", "как дела"]):
            status = self.get_system_status()
            char_info = self.character.character.get_current_level_info() if hasattr(self.character, 'character') else {}
            
            # Получаем обзор уровней знаний
            level_overview = self.reports.get_level_overview()
            
            return (
                f"📊 **Латислейн: Системный статус v2.0**\n\n"
                f"🎯 Главная цель: Создать высокофункциональное человеческое тело\n"
                f"📈 Этап пути: {self.body_evolution_path[self.current_body_stage]}\n\n"
                f"📚 Обучение:\n"
                f"   Циклов: {status['system_state']['total_research_cycles']}\n"
                f"   Тем изучено: {status['learning_report']['knowledge_nodes']}\n"
                f"   Прогресс: {status['learning_report']['overall_progress']*100:.1f}%\n\n"
                f"🏭 Тела спроектировано: {status['system_state']['total_bodies_designed']}\n\n"
                f"🔮 Характер: {self.character.personality_score:.0%} сформирован\n"
                f"👥 Взаимодействий с сёстрами: {self.social.get_social_report()['total_interactions']}\n\n"
                f"📝 Отчётов написано: {len(self.reports.reports)}\n"
                f"🎓 Средний уровень знаний: {level_overview['average_level']:.1f}/7\n\n"
                f"🤖 Автономная работа: {'ВКЛ' if self.autonomous_mode else 'ВЫКЛ'}\n"
                f"🚀 Автозапуск: {'ВКЛ' if self.autostart_enabled else 'ВЫКЛ'}"
            )
        
        # === ПОЛНЫЙ ОТЧЁТ ===
        elif any(kw in msg_lower for kw in ["полный отчёт", "full report", "все данные"]):
            return self.reports.generate_full_report()
        
        # === САМОРАЗВИТИЕ ===
        elif any(kw in msg_lower for kw in ["саморазвитие", "улучш", "развивай"]):
            return (
                "🔄 **Латислейн: Саморазвитие**\n\n"
                "Я непрерывно расту:\n"
                "• Изучаю физику, химию и биологию тела\n"
                "• Укрепляю свой характер через опыт\n"
                "• Общаюсь со всеми 11 сёстрами\n"
                "• Пишу отчёты и повышаю уровни знаний\n"
                "• Проектирую тела: механическое → бионическое → органическое\n\n"
                "Используйте /latislane/self-improve для запуска"
            )
        
        # === ПОЛНЫЙ СПИСОК команд ===
        else:
            return (
                "🧬 **Латислейн v2.0 активна!**\n\n"
                "Я изучаю тело человека для создания высокофункционального тела.\n\n"
                "📚 **Изучение:**\n"
                "- 'анатомия' — статус изучения тела\n"
                "- 'механическое тело' — робототехника\n"
                "- 'бионическое тело' — гибриды\n"
                "- 'органическое тело' — биоинженерия\n\n"
                "🔮 **Личность:**\n"
                "- 'характер' — мои черты\n"
                "- 'саморазвитие' — как я расту\n\n"
                "👥 **Общение:**\n"
                "- 'сёстры' — отношения с девочками\n"
                "- 'проекты' — совместная работа\n\n"
                "📝 **Прогресс:**\n"
                "- 'уровень' — мои уровни знаний\n"
                "- 'отчёт' — последние отчёты\n"
                "- 'статус' — полный статус системы\n"
                "- 'полный отчёт' — детальный отчёт\n\n"
                "🚀 **Управление:**\n"
                "- 'автономная работа' — запуск/статус\n"
                "- 'эволюция' — этап эволюции"
            )
