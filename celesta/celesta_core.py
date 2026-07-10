"""
Celesta — Ядро системы изучения интимной жизни.

Управляет:
- Модулями интимных знаний
- Интернет-обучением
- Эволюцией понимания
- Интеграцией с Pantikur
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .intimacy_modules import (
    IntimacyModule,
    IntimacyStage,
    IntimacyCategory,
    create_default_modules
)
from .intimacy_learning import IntimacyLearningEngine

logger = logging.getLogger("celesta.core")


class CelestaCore:
    """
    Основное ядро системы Селеста.
    
    Это 'мозг' системы, который:
    1. Изучает интимную жизнь всех рас
    2. Анализирует последствия каждого этапа
    3. Отслеживает эволюцию понимания
    4. Интегрируется с чат-ботом Pantikur
    """
    
    def __init__(self, project_root: str = ".", demo_mode: bool = True):
        self.project_root = Path(project_root)
        self.demo_mode = demo_mode
        
        # Директория данных
        self.data_dir = self.project_root / "data" / "celesta"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализация подсистем
        self.learning_engine = IntimacyLearningEngine(
            data_dir=str(self.data_dir / "learning")
        )
        
        # Создание модулей интимных знаний
        self.intimacy_modules = create_default_modules()
        
        # Состояние системы
        self.system_state = {
            "initialized_at": time.time(),
            "total_knowledge_points": 0,
            "total_research_cycles": 0,
            "current_focus": "touch_research",
            "integration_status": {
                "chatbot": False,
                "internet_learning": True
            }
        }
        
        # Журнал событий
        self.event_log: List[Dict[str, Any]] = []
        
        # Загрузка состояния
        self._load_state()
        
        logger.info("🌹 CelestaCore инициализирован")
        logger.info(f"   📚 Модулей интимных знаний: {len(self.intimacy_modules)}")
        logger.info(f"   🔍 Движок обучения активен")
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
                logger.info(f"✅ Состояние Селесты загружено")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки состояния: {e}")
        else:
            logger.info("ℹ️ Новое состояние Селесты создано")
    
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
    
    def start_intimacy_study(self):
        """Начать изучение интимной жизни."""
        logger.info("📖 Запуск изучения интимной жизни")
        self.system_state["current_focus"] = "intimacy_study"
        self.log_event("STUDY_STARTED", "Изучение интимной жизни начато")
        
        gaps = self.learning_engine.get_knowledge_gaps()
        
        if gaps:
            logger.info(f"🎯 Определено {len(gaps)} тем для изучения")
            self.log_event("GAPS_IDENTIFIED", f"Определено {len(gaps)} пробелов", {"topics": gaps[:5]})
        else:
            logger.info("✅ Все темы уже изучены")
        
        self._save_state()
    
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
    
    async def run_study_cycle(self, topics: Optional[List[str]] = None, batch_size: int = 3):
        """Запустить цикл обучения."""
        logger.info("🔄 Запуск цикла обучения")
        self.system_state["total_research_cycles"] += 1
        
        if topics is None:
            topics = self.learning_engine.get_knowledge_gaps()[:10]
        
        if not topics:
            logger.info("ℹ️ Нет тем для изучения")
            return
        
        results = await self.learning_engine.learn_batch(topics, batch_size)
        
        logger.info(f"✅ Цикл завершён: {results['completed']}/{results['total_topics']} тем")
        self.log_event("STUDY_CYCLE_COMPLETED", "Цикл обучения завершён", results)
        
        self._save_state()
    
    def get_intimacy_report(self) -> Dict[str, Any]:
        """Получить отчёт по изученной интимной жизни."""
        report = {
            "modules": {},
            "overall_progress": 0.0,
            "stages_coverage": {}
        }
        
        total_progress = 0.0
        stages_total = {stage: 0 for stage in IntimacyStage}
        stages_covered = {stage: 0 for stage in IntimacyStage}
        
        for name, module in self.intimacy_modules.items():
            report["modules"][name] = module.to_dict()
            total_progress += module.research_progress
            
            for stage in IntimacyStage:
                stages_total[stage] += 1
                if stage in module.stages_covered:
                    stages_covered[stage] += 1
        
        report["overall_progress"] = total_progress / len(self.intimacy_modules) if self.intimacy_modules else 0
        report["stages_coverage"] = {
            stage.value: {
                "covered": stages_covered[stage],
                "total": stages_total[stage],
                "percent": (stages_covered[stage] / stages_total[stage] * 100) if stages_total[stage] > 0 else 0
            }
            for stage in IntimacyStage
        }
        
        return report
    
    def get_stage_details(self, stage: IntimacyStage) -> Dict[str, Any]:
        """Получить детали по конкретному этапу."""
        details = {
            "stage": stage.value,
            "modules": [],
            "knowledge_points": [],
            "consequences": []
        }
        
        for name, module in self.intimacy_modules.items():
            if stage in module.stages_covered:
                for kp in module.knowledge_points:
                    if kp.get("stage") == stage.value:
                        details["modules"].append(name)
                        details["knowledge_points"].append(kp)
        
        return details
    
    def get_consequences_info(self, scenario: str) -> Dict[str, Any]:
        """
        Получить информацию о последствиях.
        
        :param scenario: Сценарий ("excessive", "interrupted", "normal")
        """
        scenario_map = {
            "excessive": IntimacyStage.EXCESSIVE,
            "interrupted": IntimacyStage.INTERRUPTED,
            "normal": IntimacyStage.POST_INTIMACY
        }
        
        stage = scenario_map.get(scenario, IntimacyStage.POST_INTIMACY)
        return self.get_stage_details(stage)
    
    def get_race_specific_info(self, race: str) -> Dict[str, Any]:
        """Получить информацию об особенностях расы."""
        race_module = self.intimacy_modules.get("race_specific_intimacy")
        if not race_module:
            return {}
        
        result = race_module.race_variants.get(race, {})
        if isinstance(result, dict):
            return result
        return {}
    
    def integrate_with_chatbot(self, chatbot_instance: Any = None):
        """Интеграция с чат-ботом Pantikur."""
        logger.info("🔗 Интеграция с чат-ботом Pantikur")
        self.system_state["integration_status"]["chatbot"] = True
        self.log_event("INTEGRATION", "Интеграция с чат-ботом завершена")
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
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить статус всей системы."""
        return {
            "system_state": self.system_state,
            "modules_count": len(self.intimacy_modules),
            "learning_report": self.learning_engine.get_learning_report(),
            "event_log_count": len(self.event_log),
            "last_events": self.event_log[-10:]
        }
    
    def chat_response(self, user_message: str) -> str:
        """Ответ на вопрос через Селесту."""
        msg_lower = user_message.lower()
        
        # Прикосновения
        if any(kw in msg_lower for kw in ["прикоснов", "touch", "касание"]):
            return self._touch_response()
        
        # Возбуждение
        elif any(kw in msg_lower for kw in ["возбужд", "arousal", "предварительн"]):
            return self._arousal_response()
        
        # Избыточный интим
        elif any(kw in msg_lower for kw in ["избыточн", "excessive", "часто", "истощени"]):
            return self._excessive_response()
        
        # Прерванный процесс
        elif any(kw in msg_lower for kw in ["прерванн", "interrupted", "останов", "задержк"]):
            return self._interrupted_response()
        
        # Последствия
        elif any(kw in msg_lower for kw in ["последств", "consequence", "эффект", "влиян"]):
            return self._consequences_response()
        
        # Восстановление
        elif any(kw in msg_lower for kw in ["восстановл", "recovery", "рефрактерн"]):
            return self._recovery_response()
        
        # Расы
        elif any(kw in msg_lower for kw in ["рас", "race", "эльф", "демон", "нежить"]):
            return self._race_response()
        
        # Статус
        elif any(kw in msg_lower for kw in ["статус", "прогресс", "как дела"]):
            return self._status_response()
        
        else:
            return (
                "🌹 **Селеста активна**\n\n"
                "Я изучаю интимную жизнь всех рас.\n\n"
                "Запросы:\n"
                "- 'прикосновения' — виды и эффекты\n"
                "- 'возбуждение' — физиология\n"
                "- 'избыточный интим' — последствия\n"
                "- 'прерванный процесс' — последствия\n"
                "- 'расы' — особенности\n"
                "- 'статус' — системный статус"
            )
    
    def _touch_response(self) -> str:
        return (
            "🤚 **Селеста: Прикосновения**\n\n"
            "Виды прикосновений:\n\n"
            "1. **Лёгкие** — активируют C-волокна, вызывают удовольствие\n"
            "   Скорость: 1 м/с\n"
            "   Эффект: окситоцин, расслабление\n\n"
            "2. **Давящие** — активируют A-дельта волокна\n"
            "   Скорость: 20 м/с\n"
            "   Эффект: ощущение давления, безопасность\n\n"
            "3. **Оральные** — 2/3 коры мозга\n"
            "   Эффект: максимальная чувствительность\n\n"
            "⚠️ Тактильная депривация (без прикосновений >3 дней):\n"
            "   - Кортизол ↑\n"
            "   - Тревожность ↑\n"
            "   - Иммунитет ↓"
        )
    
    def _arousal_response(self) -> str:
        return (
            "🔥 **Селеста: Возбуждение**\n\n"
            "Фазы возбуждения:\n"
            "1. Желание (мозговые центры)\n"
            "2. Возбуждение (парасимпатическая система)\n"
            "3. Плато (максимальное напряжение)\n"
            "4. Оргазм (симпатическая система)\n\n"
            "Физиология:\n"
            "- Эрекция/лубрикация: парасимпатические волокна\n"
            "- Нейротрансмиттер: оксид азота (NO)\n"
            "- Время реакции: 30 секунд\n\n"
            "Психология:\n"
            "- 70% возбуждения зависит от психологических факторов\n"
            "- Факторы: эмоции, доверие, стресс, окружение"
        )
    
    def _excessive_response(self) -> str:
        return (
            "⚠️ **Селеста: Избыточный интим**\n\n"
            "Последствия:\n\n"
            "1. **Истощение минералов**\n"
            "   - Цинк: потеря 3 мг за событие\n"
            "   - Восстановление: 2-3 дня\n\n"
            "2. **Гормональный дисбаланс**\n"
            "   - Пролактин ↑ → тестостерон ↓ на 25%\n"
            "   - Рефрактерный период: 12-48 часов\n\n"
            "3. **Хроническая усталость**\n"
            "   - Симптомы: усталость, раздражительность\n"
            "   - Восстановление: 3-7 дней\n\n"
            "4. **Повреждение тканей**\n"
            "   - Микроабразии\n"
            "   - Заживление: 12-24 часа\n"
            "   - Риск инфекции: высокий\n\n"
            "5. **Дофаминовая зависимость**\n"
            "   - Толерантность за недели\n"
            "   - Синдром отмены: раздражительность\n\n"
            "6. **Долгосрочные эффекты**\n"
            "   - Низкий тестостерон\n"
            "   - Высокий пролактин\n"
            "   - Восстановление: 1-3 месяца"
        )
    
    def _interrupted_response(self) -> str:
        return (
            "🚫 **Селеста: Прерванный процесс**\n\n"
            "Последствия:\n\n"
            "1. **Венозный застой**\n"
            "   - Симптомы: боль, давление, отёк\n"
            "   - Длительность: 6-24 часа\n\n"
            "2. **Резорбция семенного материала**\n"
            "   - Процесс: фагоцитоз\n"
            "   - Длительность: 2-3 дня\n"
            "   - Симптомы: давление в эпидидимисе\n\n"
            "3. **Психологический стресс**\n"
            "   - Кортизол ↑, адреналин ↑\n"
            "   - Эффекты: фрустрация, тревога\n\n"
            "4. **Ретроградная эякуляция**\n"
            "   - Риск: повреждение мочевого пузыря\n"
            "   - Долгосрочное: бесплодие\n\n"
            "5. **Хронический простатит**\n"
            "   - Симптомы: боль, дисфункция, частота\n"
            "   - Восстановление: 3-12 месяцев\n\n"
            "6. **Нарушение рефлексов**\n"
            "   - Эректильная дисфункция\n"
            "   - Преждевременная эякуляция"
        )
    
    def _consequences_response(self) -> str:
        return (
            "📊 **Селеста: Общие последствия**\n\n"
            "Позитивные:\n"
            "- Иммунитет ↑ на 30% (IgA)\n"
            "- Окситоцин ↓ тревожность\n"
            "- Эндорфины ↑ боль\n\n"
            "Негативные:\n"
            "- Стресс ↓ фертильность на 40%\n"
            "- ИМТ вне нормы ↓ качество спермы/яйцеклеток\n\n"
            "Нейтральные:\n"
            "- Рефрактерный период возрастозависимый\n"
            "- Гормональные циклы 24-28 дней"
        )
    
    def _recovery_response(self) -> str:
        return (
            "💤 **Селеста: Восстановление**\n\n"
            "Рефрактерный период:\n"
            "- Мужчины: 15 мин — 48 часов\n"
            "- Зависит от уровня пролактина\n"
            "- Возрастная зависимость: да\n\n"
            "Восстановление минералов:\n"
            "- Цинк: 2-3 дня\n"
            "- Источники: устрицы, тыквенные семечки, говядина\n"
            "- Дозировка: 15 мг/день\n\n"
            "Сон:\n"
            "- Гормон роста ↑ во сне\n"
            "- Нужно: 7 часов\n"
            "- Ускорение восстановления: 40%\n\n"
            "Гидратация:\n"
            "- Вода: 2 л/день\n"
            "- Выведение токсинов: 12 часов"
        )
    
    def _race_response(self) -> str:
        return (
            "🌍 **Селеста: Особенности по расам**\n\n"
            "1. **Люди**\n"
            "   - Стандартная физиология\n"
            "   - Цикл: 24-28 дней\n"
            "   - Фертильное окно: 5 дней\n\n"
            "2. **Эльфы**\n"
            "   - Замедленный метаболизм\n"
            "   - Фаза возбуждения ×2\n"
            "   - Чувствительность гормонов: высокая\n"
            "   - Сила связи: очень сильная\n\n"
            "3. **Демоны**\n"
            "   - Выносливость ×3\n"
            "   - Рефрактерный период ÷3\n"
            "   - Интенсивность гормонов: экстремальная\n\n"
            "4. **Нежить**\n"
            "   - Репродукция: нет\n"
            "   - Сенсорика: сохранена\n"
            "   - Гормоны: нет\n\n"
            "5. **Элементали**\n"
            "   - Механизм: энергетический обмен\n"
            "   - Физический контакт: нет\n"
            "   - Связь: телепатическая"
        )
    
    def _status_response(self) -> str:
        report = self.get_intimacy_report()
        progress = report["overall_progress"] * 100
        
        return (
            f"📊 **Селеста: Системный статус**\n\n"
            f"Изучено модулей: {len(report['modules'])}\n"
            f"Общий прогресс: {progress:.1f}%\n\n"
            f"Покрытие этапов:\n"
        ) + "\n".join(
            f"- {stage}: {data['percent']:.0f}%"
            for stage, data in list(report["stages_coverage"].items())[:5]
        )
