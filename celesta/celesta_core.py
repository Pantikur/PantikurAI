"""
Селеста — Ядро системы изучения интимной жизни.

Управляет:
- Модулями интимных знаний (Solo, Duo, Trio, Quad, Group, Same-Sex, Consent, Coercion)
- Интернет-обучением
- Эволюцией понимания
- Характером
- Взаимодействием с 11 другими девочками
- Отчётами и повышением уровней
- Автономной работой и автозапуском
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
    IntimacyCategory,
    IntimacyLevel,
    create_default_modules
)
from .intimacy_learning import IntimacyLearningEngine

logger = logging.getLogger("celesta.core")


class CelestaCore:
    """
    Основное ядро системы Селеста.
    
    Это 'мозг' системы, который:
    1. Изучает интимную жизнь ВСЕХ форм (solo, duo, trio, quad, group, same-sex)
    2. Изучает consent и coercion
    3. Отслеживает уровни знаний (0-5)
    4. Работает автономно с автозапуском
    5. Общается с 11 другими девочками
    6. Пишет отчёты
    7. Воспитывает характер
    8. Имеет доступ в интернет
    """
    
    def __init__(self, project_root: str = ".", demo_mode: bool = True):
        self.project_root = Path(project_root)
        self.demo_mode = demo_mode
        
        # === Автономность ===
        self.max_autonomy_level = "L3"
        self.autonomy_level = "L0"
        self.require_confirmation_above = "L2"
        
        # Директория данных
        self.data_dir = self.project_root / "data" / "celesta"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализация подсистем
        self.learning_engine = IntimacyLearningEngine(
            data_dir=str(self.data_dir / "learning")
        )
        
        # Создание модулей интимных знаний
        self.intimacy_modules = create_default_modules()
        
        # Характер
        self.character = self._load_character()
        
        # Уровни знаний по категориям
        self.knowledge_levels: Dict[str, int] = {
            name: 0 for name in self.intimacy_modules
        }
        
        # Состояние системы
        self.system_state = {
            "initialized_at": time.time(),
            "total_knowledge_points": 0,
            "total_research_cycles": 0,
            "current_focus": "initialization",
            "overall_knowledge_level": 0,
            "integration_status": {
                "chatbot": False,
                "internet_learning": True,
                "sisters_network": False,
                "reports": True
            }
        }
        
        # Журнал событий
        self.event_log: List[Dict[str, Any]] = []
        
        # Загрузка состояния
        self._load_state()
        
        logger.info("🌹 CelestaCore инициализирован")
        logger.info(f"   📚 Модулей интимных знаний: {len(self.intimacy_modules)}")
        logger.info(f"   🔍 Движок обучения активен")
        logger.info(f"   🌐 Автономное обучение: ВКЛ")
        logger.info(f"   👤 Характер: {self.character.get('my_character', {}).get('name', 'не выбран') if self.character else 'не выбран'}")
    
    def _load_character(self) -> Optional[Dict]:
        """Загрузить характер из my_character.yaml."""
        char_path = self.data_dir.parent / "my_character.yaml"
        if char_path.exists():
            try:
                import yaml
                with open(char_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except ImportError:
                logger.warning("PyYAML не установлен, характер не загружен")
            except Exception as e:
                logger.warning(f"Ошибка загрузки характера: {e}")
        return None
    
    def _load_state(self):
        """Загрузить состояние системы."""
        state_file = self.data_dir / "system_state.json"
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self.system_state.update(state.get("system_state", {}))
                self.event_log = state.get("event_log", [])[-100:]
                self.knowledge_levels = state.get("knowledge_levels", self.knowledge_levels)
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
            "knowledge_levels": self.knowledge_levels,
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
    
    def start_autonomous_learning(self, interval_minutes: int = 10):
        """
        Запустить автономное обучение.
        
        :param interval_minutes: Интервал между циклами (минуты)
        """
        logger.info(f"🚀 Запуск автономного обучения (интервал: {interval_minutes} мин)")
        
        self.system_state["current_focus"] = "autonomous_learning"
        self.log_event("AUTO_LEARNING_STARTED", f"Автономное обучение запущено, интервал: {interval_minutes} мин")
        
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
        
        # Обновляем уровни знаний
        self._update_knowledge_levels()
        
        logger.info(f"✅ Цикл завершён: {results['completed']}/{results['total_topics']} тем")
        self.log_event("STUDY_CYCLE_COMPLETED", "Цикл обучения завершён", results)
        
        self._save_state()
    
    def _update_knowledge_levels(self):
        """Обновить уровни знаний по модулям."""
        for name, module in self.intimacy_modules.items():
            if module.knowledge_points:
                avg_confidence = sum(
                    self.learning_engine.knowledge_nodes.get(kp["point"], 
                        type('obj', (object,), {'confidence': 0.3})()
                    ).confidence if kp["point"] in self.learning_engine.knowledge_nodes else 0.3
                    for kp in module.knowledge_points
                ) / len(module.knowledge_points)
                
                # Определяем уровень
                if avg_confidence > 0.9:
                    level = 5
                elif avg_confidence > 0.75:
                    level = 4
                elif avg_confidence > 0.6:
                    level = 3
                elif avg_confidence > 0.4:
                    level = 2
                elif avg_confidence > 0.2:
                    level = 1
                else:
                    level = 0
                
                old_level = self.knowledge_levels.get(name, 0)
                if isinstance(old_level, str):
                    old_level = int(old_level)
                self.knowledge_levels[name] = max(old_level, level)
                
                if level > old_level:
                    self.log_event("LEVEL_UP", f"Уровень {name}: {old_level} → {level}")
    
    def generate_report(self, report_type: str = "daily") -> Dict[str, Any]:
        """Сгенерировать отчёт."""
        report = {
            "type": report_type,
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "overall_progress": 0.0,
            "knowledge_levels": dict(self.knowledge_levels),
            "categories": {},
            "event_summary": [],
        }
        
        total_progress = 0.0
        category_progress = {}
        
        for name, module in self.intimacy_modules.items():
            report["modules"][name] = module.to_dict()
            total_progress += module.research_progress
            
            # Группируем по категориям
            cat = module.category.value.split("_")[0] if "_" in module.category.value else module.category.value
            if cat not in category_progress:
                category_progress[cat] = {"modules": 0, "progress": 0.0}
            category_progress[cat]["modules"] += 1
            category_progress[cat]["progress"] += module.research_progress
        
        report["overall_progress"] = total_progress / len(self.intimacy_modules) if self.intimacy_modules else 0
        report["categories"] = {
            cat: {
                "modules_count": data["modules"],
                "average_progress": data["progress"] / data["modules"] if data["modules"] > 0 else 0
            }
            for cat, data in category_progress.items()
        }
        
        report["event_summary"] = self.event_log[-20:]
        
        return report
    
    def get_system_status(self) -> Dict[str, Any]:
        """Получить статус всей системы."""
        return {
            "system_state": self.system_state,
            "modules_count": len(self.intimacy_modules),
            "knowledge_levels": dict(self.knowledge_levels),
            "character": self.character,
            "event_log_count": len(self.event_log),
            "last_events": self.event_log[-10:],
        }
    
    def chat_response(self, user_message: str) -> str:
        """Ответ на вопрос через Селесту."""
        msg_lower = user_message.lower()
        
        # Solo
        if any(kw in msg_lower for kw in ["соло", "solo", "одиночн", "мастурб", "ананизм"]):
            return self._solo_response()
        
        # Duo
        elif any(kw in msg_lower for kw in ["дуо", "duo", "два", "классик", "парная"]):
            return self._duo_response()
        
        # Trio
        elif any(kw in msg_lower for kw in ["трио", "trio", "трое", "2f1m", "2m1f"]):
            return self._trio_response()
        
        # Group
        elif any(kw in msg_lower for kw in ["групп", "group", "орги", "оргия"]):
            return self._group_response()
        
        # Same-Sex
        elif any(kw in msg_lower for kw in ["однопол", "same-sex", "lesbian", "gay", "мужчина мужчина", "женщина женщина"]):
            return self._ss_response()
        
        # Consent
        elif any(kw in msg_lower for kw in ["согласие", "consent", "fries", "yes"]):
            return self._consent_response()
        
        # Coercion
        elif any(kw in msg_lower for kw in ["принужд", "coercion", "манипуляц", "газлайт", "красн"]):
            return self._coercion_response()
        
        # Status
        elif any(kw in msg_lower for kw in ["статус", "прогресс", "как дела", "report"]):
            return self._status_response()
        
        # Pose/Position
        elif any(kw in msg_lower for kw in ["поз", "position", "миссионер", "догги", "наездниц", "69"]):
            return self._positions_response()
        
        # Fetishes
        elif any(kw in msg_lower for kw in ["фетиш", "fetish", "бдсМ", "bdsM", "доминирован"]):
            return self._fetish_response()
        
        else:
            return (
                "🌹 **Селеста активна**\n\n"
                "Я изучаю интимную жизнь ВСЕХ форм.\n\n"
                "Запросы:\n"
                "- 'соло' — одиночные практики, фетиши, игрушки\n"
                "- 'дуо' — классика, все позы, все техники\n"
                "- 'трио' — тройные взаимодействия\n"
                "- 'групп' — оргии, групповые практики\n"
                "- 'однопол' — M|M, F|F\n"
                "- 'согласие' — все формы согласия\n"
                "- 'принужд' — для защиты\n"
                "- 'поз' — все позы\n"
                "- 'фетиш' — фетиши и БДСМ\n"
                "- 'статус' — системный статус"
            )
    
    # ================================================================
    #  ОТВЕТЫ ПО КАТЕГОРИЯМ
    # ================================================================
    
    def _solo_response(self) -> str:
        return (
            "🤚 **Селеста: Solo (Одиночные практики)**\n\n"
            "Категории solo:\n\n"
            "1. **Мастурбация** — нормальная практика (95%+ людей)\n"
            "   Техники: клиторальная, пенальная, G-точка, анальная\n\n"
            "2. **Фетиши соло** — визуальные, тактильные, ролевые\n"
            "   Сены, материалы (латекс, шёлк, кожа)\n\n"
            "3. **Секс-игрушки** — вибраторы, мастурбаторы, анальные\n"
            "   Типы: bullet, wand, rabbit, suction, Tenga, Fleshlight\n\n"
            "⚠️ Физиология:\n"
            "   - Потеря цинка: 3 мг за эякуляцию\n"
            "   - Восстановление: 2-3 дня\n"
            "   - POIS: редкий синдром после эякуляции"
        )
    
    def _duo_response(self) -> str:
        return (
            "💑 **Селеста: Duo (Классика)**\n\n"
            "Все позы и техники:\n\n"
            "1. **Миссионерская** — классика, вариации (ноги на плечах, подушка)\n"
            "2. **Догги-стайл** — самая глубокая поза\n"
            "3. **Наездница** — контроль седящей\n"
            "4. **Ложка** — нежная, для долгого секса\n"
            "5. **69** — одновременный оральный\n"
            "6. **Край кровати** — стоящий + лежащая\n"
            "7. **Стоя** — у стены, в душе\n\n"
            "Оральные техники:\n"
            "   - Куннилингус: клитор (8000+ нервов)\n"
            "   - Фелляция: deepthroat, hand_only, edging\n"
            "   - Анальный оральный: дама-чек обязателен\n\n"
            "Edging & Denial:\n"
            "   - Остановка перед оргазмом для усиления"
        )
    
    def _trio_response(self) -> str:
        return (
            "👥 **Селеста: Trio (Тройные)**\n\n"
            "Комбинации:\n\n"
            "1. **FFM (2F1M)** — классическая динамика, роль третьего\n"
            "2. **MMF (2M1F)** — мужская динамика, кооперация vs конкуренция\n"
            "3. **FFF (3F)** — нежность, оральные практики, трибандизм\n"
            "4. **MMM (3M)** — анальные практики, массаж, эмоциональная связь\n\n"
            "⚠️ Правила трио:\n"
            "   - Обсуждение ДО, проверка ВО ВРЕМЯ, aftercare ПОСЛЕ\n"
            "   - Управление ревностью — обязательно\n"
            "   - Кондомы и барьеры"
        )
    
    def _group_response(self) -> str:
        return (
            "🎉 **Селеста: Group (Групповые)**\n\n"
            "Типы оргий:\n"
            "1. **Мягкая** — только оральный/мануальный\n"
            "2. **Жёсткая** — проникающий\n"
            "3. **Смешанная** — обе\n\n"
            "Правила безопасности:\n"
            "   - Барьеры для всех\n"
            "   - Safe words\n"
            "   - Medical first-aid kit\n"
            "   - STD testing recommended\n\n"
            "Групповая динамика:\n"
            "   - Доминанты и аутсайдеры\n"
            "   - Ротационные паттерны\n"
            "   - Aftercare для каждого"
        )
    
    def _ss_response(self) -> str:
        return (
            "🏳️‍🌈 **Селеста: Same-Sex**\n\n"
            "Женщины+Женщины:\n"
            "1. Трибандизм (scissoring) — трение половых органов\n"
            "2. Мануальные — two-finger, G-точка\n"
            "3. Игрушки — shared vibrator, strap-on\n"
            "4. Эмоциональная составляющая — нежность, связь\n\n"
            "Мужчины+Мужчины:\n"
            "1. Анальный — подготовка, лубриканты, простата\n"
            "2. Оральный — deepthroat, hand-assisted\n"
            "3. Beauty rest — после оргазма одного, стимуляция другого\n"
            "4. Sports — standing, силовые элементы\n"
            "5. Эмоциональная — уязвимость, trust"
        )
    
    def _consent_response(self) -> str:
        return (
            "✅ **Селеста: Consent (Согласие)**\n\n"
            "FRIES — 5 критериев согласия:\n"
            "1. **F**ree — свободное, без давления\n"
            "2. **I**nformed — информированное\n"
            "3. **E**nthusiastic — энтузиастическое (не просто «не нет»)\n"
            "4. **R**eversible — обратимое (можно отозвать)\n"
            "5. **S**pecific — конкретное (да на одно ≠ да на всё)\n\n"
            "Вербальные маркеры: «да», «please», «more», «don't stop»\n"
            "Невербальные: кивок, притягивание, стон, открытая поза\n\n"
            "ONGOING consent — проверка «как тебе?» каждые 5-10 мин"
        )
    
    def _coercion_response(self) -> str:
        return (
            "🚨 **Селеста: Coercion (Принуждение — ДЛЯ ЗАЩИТЫ)**\n\n"
            "Красные флаги:\n"
            "1. **Манипуляции** — guilt-tripping, bargaining, love-bombing\n"
            "2. **Газлайтинг** — «этого не было», «ты выдумываешь»\n"
            "3. **Давление** — persistent asking после «нет»\n"
            "4. **Игнорирование границ** — первое нарушение = красный флаг\n\n"
            "Действия:\n"
            "   - Safe exit plan\n"
            "   - Документирование\n"
            "   - Терапия и поддержка\n"
            "   - Горячие линии кризисной помощи\n\n"
            "⚠️ Изучение принуждения — для защиты, не для одобрения."
        )
    
    def _positions_response(self) -> str:
        return (
            "📍 **Селеста: Позы и техники**\n\n"
            "Классические:\n"
            "1. Миссионерская — глубина: средняя, eye contact: да\n"
            "2. Догги-стайл — глубина: максимальная, eye contact: нет\n"
            "3. Наездница — глубина: контроль седящей, eye contact: да\n"
            "4. Ложка — глубина: неглубокая, intimacy: максимальная\n"
            "5. 69 — одновременный оральный, coordination:需要同步\n\n"
            "Продвинутые:\n"
            "6. Край кровати — standing + supine\n"
            "7. Стоя — у стены, в душе\n"
            "8. Lotus — сидя лицом к лицу, максимальная интимность"
        )
    
    def _fetish_response(self) -> str:
        return (
            "🎭 **Селеста: Фетиши и БДСМ**\n\n"
            "Категории фетишей:\n"
            "1. **Визуальные** — порнография, erotica, фэнтези\n"
            "2. **Тактильные** — латекс, кожа, шёлк, мех\n"
            "3. **Аудиальные** — звук, шёпот, команды\n"
            "4. **Ролевые** — doctor/patient, teacher/student\n\n"
            "БДСМ фреймворки:\n"
            "1. **SSC** — Safe, Sane, Consensual\n"
            "2. **RACK** — Risk-Aware Consensual Kink\n\n"
            "Power dynamics:\n"
            "   - D/s, Master/slave, Top/bottom\n"
            "   - Safe words: красный/жёлтый/зелёный"
        )
    
    def _status_response(self) -> str:
        report = self.generate_report("status")
        progress = report["overall_progress"] * 100
        
        return (
            f"📊 **Селеста: Системный статус**\n\n"
            f"Изучено модулей: {len(report['modules'])}\n"
            f"Общий прогресс: {progress:.1f}%\n"
            f"Циклов обучения: {self.system_state['total_research_cycles']}\n\n"
            f"Уровни знаний:\n"
        ) + "\n".join(
            f"   {name}: Уровень {level}"
            for name, level in list(self.knowledge_levels.items())[:10]
        )
    
    def integrate_with_sisters(self):
        """Интеграция с 11 другими девочками."""
        logger.info("🔗 Интеграция с сёстрами")
        self.system_state["integration_status"]["sisters_network"] = True
        self.log_event("INTEGRATION", "Интеграция с сёстрами завершена")
        self._save_state()
    
    def integrate_with_chatbot(self, chatbot_instance: Any = None):
        """Интеграция с чат-ботом Pantikur."""
        logger.info("🔗 Интеграция с чат-ботом Pantikur")
        self.system_state["integration_status"]["chatbot"] = True
        self.log_event("INTEGRATION", "Интеграция с чат-ботом завершена")
        self._save_state()
    
    async def self_improve(self):
        """Саморазвитие: анализ слабых мест и улучшение знаний."""
        logger.info("🔄 Запуск саморазвития...")
        
        # 1. Анализ пробелов
        gaps = self.learning_engine.get_knowledge_gaps()
        
        if gaps:
            logger.info(f"📚 Изучение {len(gaps)} новых тем...")
            await self.run_study_cycle(topics=gaps[:5], batch_size=3)
        
        # 2. Обновление низкой уверенности
        low_confidence_nodes = [
            node for node in self.learning_engine.knowledge_nodes.values()
            if node.confidence < 0.5
        ]
        
        if low_confidence_nodes:
            logger.info(f"🔄 Обновление {len(low_confidence_nodes)} узлов...")
            for node in low_confidence_nodes[:5]:
                if self.learning_engine.web_researcher:
                    research = await self.learning_engine.web_researcher.learn_from_search(node.topic)
                    if research and research.get("facts"):
                        node.confidence = min(1.0, node.confidence + 0.2)
                        node.is_verified = True
        
        self._update_knowledge_levels()
        self._save_state()
        logger.info("✅ Саморазвитие завершено")
