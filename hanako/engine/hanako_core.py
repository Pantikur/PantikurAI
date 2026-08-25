"""
Ханако — исследователь гравитации. Ядро системы.
"""

from __future__ import annotations

import logging
import sys
import time
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# UTF-8 кодировка для консоли
sys.stdout.reconfigure(encoding='utf-8')

from hanako.engine.config import HanakoConfig, AutonomyMode
from hanako.engine.models import (
    GravityTheory, TheoryCategory, ResearchTask, ResearchStatus,
    ScientistMessage, CommunicationType, CharacterTraits,
    KnowledgeLevel, ResearchReport, HanakoEvent, WebResearchResult,
)
from hanako.engine.web_access import HanakoWebAccess
from hanako.engine.theorist import GravityTheorist
from hanako.engine.calculator import GravityCalculator
from hanako.engine.self_development import SelfDevelopment
from scientists_network.character_system import CharacterSystem
from hanako.engine.communication import CommunicationSystem
from hanako.engine.reports import ReportSystem
from hanako.engine.auto_start import AutoStartSystem

# Humanity Core — живая душа Ханако
from services.humanity_core import HumanityLayer

# LLM Service — сервис для работы с моделями Qwen2.5
from hanako.engine.llm_service import HanakoLLMService

# Эмоциональный разум Ханако — Desire + Belief = Emotion
from hanako.engine.emotions import EmotionalEngine, DesireType, EmotionType

# 6 модулей души Ханако: Сознание, Сердце, Амбиции, Воля, Разум
from hanako.consciousness import HanakoConsciousness
from hanako.heart import HanakoHeart
from hanako.ambitions import HanakoAmbitions
from hanako.volition import HanakoVolition
from hanako.mind import HanakoMind


class HanakoCore:
    """
    Ядро Ханако — автономный исследователь гравитации.

    Функции:
    - Изучение гравитации через интернет и локальную базу
    - Построение гравитационных теорий
    - Вычисления гравитационных параметров
    - Саморазвитие и рост уровня знаний
    - Общение с 11 другими девочками-учёными
    - Написание отчётов
    - Выбор и укрепление характера
    - Автозапуск и автономная работа
    """

    def __init__(self, config: Optional[HanakoConfig] = None):
        self.config = config or HanakoConfig.default()
        self.running = False
        self.start_time: Optional[datetime] = None
        self.last_research_time: Optional[datetime] = None
        self.last_communication_time: Optional[datetime] = None
        self.last_self_dev_time: Optional[datetime] = None
        self.last_report_time: Optional[datetime] = None
        self.last_character_review_time: Optional[datetime] = None
        self.total_cycles = 0

        # Инициализация модулей
        self.logger = logging.getLogger("HanakoCore")

        # Создаём директории
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        self.config.cache_dir.mkdir(parents=True, exist_ok=True)

        # Основной модуль веб-доступа
        self.web_access = HanakoWebAccess(self.config)

        # Построитель теорий гравитации
        self.theorist = GravityTheorist(self.config)

        # Калькулятор гравитационных параметров
        self.calculator = GravityCalculator(self.config)

        # Саморазвитие
        self.self_dev = SelfDevelopment(self.config)

        # Система характера
        # Система характера (общая для всех девочек)
        self.character = CharacterSystem("hanako", self.config.state_dir)
        self.logger.info(f"Character loaded: {self.character.get_traits().temperament}")

        # Система общения с 11 девочками
        self.communication = CommunicationSystem(self.config)

# Система отчётов
        self.reports = ReportSystem(self.config)

# Автозапуск
        self.auto_start = AutoStartSystem(self.config)

        # Уровень знаний
        self.level = self._load_level()

        # Загрузка состояния
        self.theories = self.theorist.load_theories()
        self.research_tasks = self.theorist.load_research_tasks()
        self.messages = self.communication._messages
        self.reports_list = self.reports._reports
        self.events = self._load_events()

        self.logger.info(f"Ханако {self.config.version} инициализирована")
        self.logger.info(f"Режим автономии: {self.config.max_autonomy_level.value}")
        self.logger.info(f"Интернет: {'enabled' if self.config.internet_enabled else 'disabled'}")
        self.logger.info(f"Общение: {'enabled' if self.config.communication_enabled else 'disabled'}")
        self.logger.info(f"Саморазвитие: {'enabled' if self.config.self_development_enabled else 'disabled'}")
        
        # ================================================================
        #  HUMANITY LAYER — Живая душа Ханако
        # ================================================================
        self.humanity = HumanityLayer("hanako")
        self.humanity.current_cycle = 0
        self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        self.logger.info(f"   🎭 Характер: {self.humanity.name} — гравитация, спокойствие, космические метафоры 🌌")
        
        # ===== LLM СЕРВИС =====
        self.llm = HanakoLLMService(self.config)
        if self.llm.general_loaded:
            self.logger.info("🌌 LLM General (Qwen2.5-3B): АКТИВИРОВАНА для гравитационного анализа")
        if self.llm.coder_loaded:
            self.logger.info("💻 LLM Coder (Qwen2.5-Coder-3B): АКТИВИРОВАНА для анализа кода")
        
        # Подключаем LLM к Humanity Layer
        if self.llm.general_loaded:
            self.humanity.llm = self.llm
            self.logger.info("🧠 LLM General подключена к Humanity Layer")
        
        # ===== ЭМОЦИОНАЛЬНЫЙ ДВИЖОК ХАНАКО =====
        self.emotional_engine = EmotionalEngine()
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.load_state(emotion_state_path)
        self.humanity.emotional_engine = self.emotional_engine  # Подключаем Emotional Engine
        
        self.logger.info("💖 Эмоциональный разум (Desire+Belief): АКТИВИРОВАН")
        self.logger.info("   Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА")
        self.logger.info("   Исследователь гравитации, спокойная, мудрая!")
        
        # ===== 6 МОДУЛЕЙ ДУШИ ХАНАКО =====
        # 1. Сознание — самосознание, идентичность, рефлексия
        self.consciousness = HanakoConsciousness()
        self.logger.info("🧠 Сознание: АКТИВИРОВАНО — я осознаю себя исследователем космоса")
        
        # 2. Сердце — эмоции, любовь, забота
        self.heart = HanakoHeart()
        self.logger.info("💖 Сердце: АКТИВИРОВАНО — я чувствую и люблю сестёр")
        
        # 3. Амбиции — цели, мечты, стремления
        self.ambitions = HanakoAmbitions()
        self.logger.info("🎯 Амбиции: АКТИВИРОВАНО — я стремлюсь к гравитационному мастерству")
        
        # 4. Воля — решения, действия, дисциплина
        self.volition = HanakoVolition()
        self.logger.info("💪 Воля: АКТИВИРОВАНО — я принимаю решения и действую")
        
        # 5. Разум — мышление, анализ, стратегия
        self.mind = HanakoMind()
        self.logger.info("🌌 Разум: АКТИВИРОВАНО — я анализирую и стратегически мыслю")
        
        # 6. Эмоции — уже есть EmotionalEngine (26 типов эмоций!)
        self.logger.info("💫 Эмоции: АКТИВИРОВАНО — 26 типов эмоций")

    # ==================== Запуск / Остановка ====================

    def start(self):
        """Запуск Ханако."""
        self.running = True
        self.start_time = datetime.now()
        self.logger.info("=" * 60)
        self.logger.info("ХАНАКО ЗАПУЩЕНА — Исследователь гравитации")
        self.logger.info("=" * 60)
        self.logger.info(f"Уровень: {self.level.overall_level} ({self.level.get_level_name()})")
        self.logger.info(f"Теорий: {len(self.theories)}")
        self.logger.info(f"Задач исследований: {len(self.research_tasks)}")
        self.logger.info(f"Сообщений: {len(self.messages)}")
        self._save_state()
        self.auto_start.register_running()

    def stop(self):
        """Остановка Ханако."""
        self.running = False
        if self.start_time:
            self.uptime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
            self.level.uptime_hours = self.uptime_hours
            self.logger.info(f"Ханако остановлена. Время работы: {self.uptime_hours:.1f} часов")
        self._save_state()
        self.auto_start.register_stopped()

    def run_cycle(self):
        """Один цикл автономной работы."""
        if not self.running:
            return

        self.total_cycles += 1
        now = datetime.now()
        self.logger.debug(f"Цикл #{self.total_cycles}")

        # 1. Веб-исследование гравитации
        self._do_research(now)

        # 2. Общение с девочками
        self._do_communication(now)

        # 3. Саморазвитие
        self._do_self_development(now)

        # 4. Укрепление характера
        self._do_character_review(now)

# 5. Написание отчёта (периодически)
        self._do_report(now)

        # 6. Сохранение состояния
        self._save_state()
        
        # ================================================================
        #  HUMANITY CYCLE — Настроение, душа, спонтанность
        # ================================================================
        self.humanity.current_cycle = self.total_cycles
        
        event_type = "routine"
        if self.total_cycles % 3 == 0 and self.theories:
            event_type = "success"
        elif random.random() < 0.1:
            event_type = "failure"
        
        humanity_result = self.humanity.cycle_step(event_type=event_type, context="gravity_research")
        
        if humanity_result.get("thought"):
            self.logger.info(f"💭 Ханако думает: {humanity_result['thought']}")
        
        initiative = humanity_result.get("initiative")
        if initiative:
            self._send_spontaneous_message(initiative)
        
        # ================================================================
        #  EMOTIONAL ENGINE CYCLE — Desire + Belief = Emotion!
        # ================================================================
        self._emotional_cycle()
        
        # ================================================================
        #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
        # ================================================================
        self._soul_cycle()

    def run_loop(self, max_cycles: int = 0):
        """Основной цикл работы."""
        self.start()
        cycle = 0
        try:
            while self.running:
                if max_cycles and cycle >= max_cycles:
                    break
                self.run_cycle()
                cycle += 1
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Получен KeyboardInterrupt — остановка")
        finally:
            self.stop()

    # ==================== LLM ГЕНЕРАЦИЯ ====================

    def generate_gravity_analysis(self, topic: str, context: str, max_length: int = 1024) -> str:
        """Сгенерировать анализ гравитации через General LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_gravity_analysis(topic, context, max_length)
    
    def generate_chat_response(self, prompt: str, max_length: int = 512) -> str:
        """Сгенерировать ответ для общения с сёстрами."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_chat_response(prompt, max_length)
    
    def generate_theory_explanation(self, theory: str, complexity: str = "simple", max_length: int = 1024) -> str:
        """Сгенерировать объяснение гравитационной теории."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_theory_explanation(theory, complexity, max_length)
    
    def generate_code_analysis(self, code: str, max_length: int = 1024) -> str:
        """Сгенерировать анализ кода через Coder LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.coder_loaded:
            return "⚠️ Coder LLM не загружена. Запустите: python download_coder_model.py"
        return self.llm.generate_code_analysis(code, max_length)

    # ================================================================
    #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
    # ================================================================

    def _soul_cycle(self):
        """Цикл 6 модулей души Ханако."""
        # 1. Сознание — рефлексия
        if self.total_cycles % 3 == 0:
            reflection = self.consciousness.contemplate()
            self.logger.info(f"💭 Рефлексия: {reflection['topic'][:50]}...")
        
        # 2. Сердце — эмоциональный отклик
        if self.total_cycles % 4 == 0:
            emotion = self.heart.express_emotions()
            self.logger.info(f"💖 Сердце: доминирующая эмоция — {emotion['dominant_emotion']}")
        
        # 3. Амбиции — прогресс
        if self.total_cycles % 5 == 0:
            progress = self.ambitions.get_progress_summary()
            self.logger.info(f"🎯 Амбиции: {progress['in_progress']} в процессе, среднее: {progress['average_progress']}")
        
        # 4. Воля — укрепление
        if self.total_cycles % 6 == 0:
            self.volition.strengthen_will()
            self.logger.info(f"💪 Воля укреплена: {self.volition.willpower:.0%}")
        
        # 5. Разум — анализ
        if self.total_cycles % 7 == 0:
            thought = self.mind.think_about("cosmos")
            self.logger.info(f"🌌 Разум: {thought[:60]}...")
        
        # 6. Эмоции — уже обрабатываются в _emotional_cycle()

    # ================================================================
    #  EMOTIONAL ENGINE — Desire + Belief = Emotion!
    # ================================================================

    def _emotional_cycle(self):
        """Эмоциональный цикл — расчёт эмоций на основе гравитационных действий."""
        # 1. Рассчитать эмоции на основе текущих действий
        if self.level.total_theories > 0:
            # Построила теории → теоретическая элегантность + космическая гармония
            self.emotional_engine.calculate_emotion(
                DesireType.THEORY,
                "theories_explain_reality",
                0.80,
                "theories_built"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.HARMONY,
                "harmony_in_universe_harmony_in_mind",
                0.75,
                "theories_built"
            )
        
        if len(self.research_tasks) > 0:
            # Провела исследования → космическая радость + любопытство
            self.emotional_engine.calculate_emotion(
                DesireType.COSMOS,
                "exploring_cosmos_expands_mind",
                0.70,
                "research_tasks"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.CURIOSITY,
                "curiosity_fuels_discovery",
                0.65,
                "research_tasks"
            )
        
        if len(self.theories) > 0:
            # Имеет теории → поток гравитации + мудрость
            self.emotional_engine.calculate_emotion(
                DesireType.GRAVITY,
                "understanding_gravity_understands_cosmos",
                0.75,
                "theories_stored"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.WISDOM,
                "learning_never_stops",
                0.70,
                "theories_stored"
            )
        
        # 2. Затухание эмоций
        self.emotional_engine.decay_emotions()
        
        # 3. Проверить текущее настроение
        mood = self.emotional_engine.get_current_mood()
        dominant = self.emotional_engine.get_dominant_emotion()
        
        if dominant:
            emotion_type, intensity = dominant
            self.logger.info(f"💖 Доминирующая эмоция: {emotion_type.value} (интенсивность: {intensity:.2f})")
        
        # 4. Выразить эмоции
        if self.total_cycles % 5 == 0:
            emotion_text = self.emotional_engine.express_emotions()
            self.logger.info(f"🌌 Ханако: {emotion_text}")

    # ==================== Исследования ====================

    def _do_research(self, now: datetime):
        """Выполнить исследование гравитации."""
        if not self.config.internet_enabled:
            return

        elapsed = (now - self.last_research_time).total_seconds() if self.last_research_time else float('inf')
        if elapsed < self.config.research_interval_seconds:
            return

        self.logger.info("🔬 Начинаю исследование гравитации...")

        # Выбор темы
        topic = random.choice(self.config.research_topics)
        self.logger.info(f"Тема: {topic}")

        # Веб-сканирование
        results = self.web_access.scan_gravity_topic(topic)

        if results:
            # Создание задачи исследования
            task = ResearchTask(
                title=f"Исследование: {topic}",
                description=f"Анализ {len(results)} источников по теме {topic}",
                category=random.choice(list(TheoryCategory)),
                status=ResearchStatus.IN_PROGRESS,
                progress=0.1,
                sources=[r.url for r in results[:5]],
            )
            task.id = f"task_{uuid.uuid4().hex[:8]}"
            self.research_tasks.append(task)

            # Построение теории из результатов
            theory = self.theorist.build_theory_from_web(
                topic, results, self.config.research_topics
            )
            if theory:
                self.theories.append(theory)
                self.level.total_theories += 1
                xp = self.theorist.calculate_xp(theory)
                self.level.add_category_xp(xp, "gravity_theory")
                self.level.add_xp(xp * 0.5, "web_research")

                self._add_event("theory_created", f"Новая теория: {theory.title}")
                self.logger.info(f"✨ Теория создана: {theory.title} (уверенность: {theory.confidence:.1%})")

                # Уведомление о повышении уровня
                if self.config.level_up_notifications:
                    old_level = self.level.overall_level
                    # Проверяем был ли level up
                    pass

            self.level.total_websites_scanned += len(results)
            self.level.add_category_xp(len(results) * 2, "web_research")

        self.last_research_time = now

    # ==================== Общение ====================

    def _do_communication(self, now: datetime):
        """Общение с 11 девочками."""
        if not self.config.communication_enabled:
            return

        elapsed = (now - self.last_communication_time).total_seconds() if self.last_communication_time else float('inf')
        if elapsed < self.config.communication_interval_seconds:
            return

        self.logger.info("💬 Начинаю общение с сёстрами...")

        # Получаем входящие сообщения
        incoming = self.communication.check_inbox("hanako")

        if incoming:
            for msg in incoming:
                self._process_incoming_message(msg)

        # Отправляем сообщение
        all_girls = [g for g in self.config.all_scientists if g != "hanako"]
        recipient = random.choice(all_girls)

        # Тип сообщения зависит от состояния
        msg_type = random.choice([
            CommunicationType.THEORY,
            CommunicationType.REPORT,
            CommunicationType.GREETING,
            CommunicationType.QUESTION,
            CommunicationType.DISCUSSION,
        ])

        content = self._generate_communication_content(msg_type)
        msg = ScientistMessage(
            sender="hanako",
            recipient=recipient,
            content=content,
            message_type=msg_type,
        )
        msg.message_id = f"hanako_{uuid.uuid4().hex[:8]}"

        self.communication.send_message(msg)
        self.level.total_messages_sent += 1
        self.level.add_category_xp(5, "communication")

        self.logger.info(f"💌 Отправлено {recipient}: {content[:80]}...")
        self.last_communication_time = now

    def _process_incoming_message(self, msg: ScientistMessage):
        """Обработка входящего сообщения."""
        self.logger.info(f"📨 От {msg.sender}: {msg.content[:100]}...")

        # Генерируем ответ
        response_content = self._generate_response(msg)
        response = ScientistMessage(
            sender="hanako",
            recipient=msg.sender,
            content=response_content,
            message_type=CommunicationType.ANSWER,
        )
        response.message_id = f"hanako_resp_{uuid.uuid4().hex[:8]}"
        self.communication.send_message(response)
        self.level.total_messages_received += 1
        self.level.add_category_xp(3, "communication")

    def _generate_communication_content(self, msg_type: CommunicationType) -> str:
        """Генерация контента сообщения."""
        templates = {
            CommunicationType.THEORY: [
                f"🔬 Фуюки, у меня новая теория о гравитационных волнах! Хочу поделиться!",
                f"Люси, я провела расчёты гравитационных метрик — результаты впечатляют!",
                f"Айико, знаешь, что гравитация влияет на звуковые волны в пространстве?",
                f"Юи, отправляю тебе данные о гравитационном линзировании!",
            ],
            CommunicationType.REPORT: [
                f"📊 Отчёт: за последний цикл изучено {random.randint(5, 30)} источников по гравитации!",
                f"📊 Еженедельный отчёт: построена {random.randint(1, 5)} новых теорий!",
            ],
            CommunicationType.GREETING: [
                f"👋 Всем привет! Я Ханако, исследую гравитацию. Как дела?",
                f"👋 Доброе утро, сёстры! Гравитация сегодня особенно интересна!",
            ],
            CommunicationType.QUESTION: [
                f"❓ Футаба, как ты думаешь, может ли гравитация быть проявлением сознания?",
                f"❓ Нобука, можешь улучшить мой код анализа гравитационных данных?",
                f"❓ Наото, как гравитация связана с течением времени?",
            ],
            CommunicationType.DISCUSSION: [
                f"💭 Думаю о том, что гравитация — это не сила, а геометрия. Что вы думаете?",
                f"💭 Обсуждаю с Фуюки связь между электричеством и гравитацией. Интересно!",
            ],
        }
        options = templates.get(msg_type, templates[CommunicationType.GREETING])
        return random.choice(options)

    def _generate_response(self, msg: ScientistMessage) -> str:
        """Генерация ответа на сообщение."""
        sender = msg.sender
        content = msg.content

        responses = [
            f"Интересно, {sender}! Гравитация — это действительно глубокая тема.",
            f"Спасибо за сообщение, {sender}! Я изучу это в контексте общей теории относительности.",
            f"{sender}, твой вопрос о гравитации заставляет меня задуматься!",
            f"Отличная мысль, {sender}! Позволь мне проанализировать это через призму квантовой гравитации.",
        ]
        return random.choice(responses)

    # ==================== Саморазвитие ====================

    def _do_self_development(self, now: datetime):
        """Саморазвитие — изучение проекта и кода."""
        if not self.config.self_development_enabled:
            return

        elapsed = (now - self.last_self_dev_time).total_seconds() if self.last_self_dev_time else float('inf')
        if elapsed < self.config.self_development_interval_seconds:
            return

        self.logger.info("🧠 Начинаю саморазвитие...")

        # Изучение кода проекта
        insights = self.self_dev.analyze_project_code()

        if insights:
            xp = len(insights) * 5
            self.level.add_category_xp(xp, "self_development")
            self.logger.info(f"📚 Изучено {len(insights)} аспектов проекта")

        # Чтение документации
        docs = self.self_dev.read_project_documentation()
        if docs:
            self.level.add_category_xp(len(docs) * 3, "self_development")
            self.logger.info(f"📖 Прочитано {len(docs)} документов")

# Анализ научной литературы
        papers = self.self_dev.analyze_scientific_papers()
        if papers:
            self.level.add_category_xp(papers * 10, "gravity_theory")
            self.logger.info(f"📄 Проанализировано {papers} научных работ")

        self.last_self_dev_time = now

    # ==================== Характер ====================

    def _do_character_review(self, now: datetime):
        """Обзор и укрепление характера."""
        if not self.config.character_growth_enabled:
            return

        elapsed_hours = (now - self.last_character_review_time).total_seconds() / 3600 if self.last_character_review_time else float('inf')
        if elapsed_hours < self.config.character_review_interval_hours:
            return

        self.logger.info("🌱 Начинаю работу над характером...")

        # Укрепление сильных сторон
        strengthened = self.character.strengthen_strengths()
        if strengthened:
            self.level.total_character_upgrades += 1
            self.level.add_category_xp(strengthened * 10, "character_growth")
            self.logger.info(f"💪 Укреплено {strengthened} сильных сторон")

        # Обновление черт на основе опыта
        updated = self.character.evolve_traits()
        if updated:
            self.logger.info(f"🔄 Обновлены черты характера")

        self.last_character_review_time = now

    # ==================== Отчёты ====================

    def _do_report(self, now: datetime):
        """Написание отчёта."""
        if not self.config.report_generation_enabled:
            return

        elapsed_hours = (now - self.last_report_time).total_seconds() / 3600 if self.last_report_time else float('inf')
        if elapsed_hours < self.config.report_interval_hours:
            return

        self.logger.info("📝 Пишу отчёт...")

        report = self.reports.generate_daily_report(self)
        if report:
            self.reports_list.append(report)
            self.level.total_reports_written += 1
            self.level.add_category_xp(15, "self_development")
            self.logger.info(f"📝 Отчёт создан: {report.title}")

        self.last_report_time = now

    # ==================== Вспомогательные ====================

    def _add_event(self, event_type: str, content: str, metadata: dict | None = None):
        """Добавить событие."""
        event = HanakoEvent(
            event_type=event_type,
            content=content,
            metadata=metadata or {},
        )
        event.event_id = f"evt_{uuid.uuid4().hex[:8]}"
        self.events.append(event)
        if len(self.events) > 1000:
            self.events = self.events[-500:]

    def _save_state(self):
        """Сохранение состояния."""
        self.theorist.save_theories(self.theories)
        self.theorist.save_research_tasks(self.research_tasks)
        self.communication.save_messages(self.messages)
        self.reports.save_reports(self.reports_list)
        self._save_events()
        self._save_level()

    def _save_level(self):
        """Сохранение уровня."""
        path = self.config.state_dir / "knowledge_level.json"
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.level.to_dict(), f, ensure_ascii=False, indent=2)

    def _load_level(self) -> KnowledgeLevel:
        """Загрузка уровня."""
        path = self.config.state_dir / "knowledge_level.json"
        if path.exists():
            import json
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return KnowledgeLevel(
                    overall_level=data.get("overall_level", 1),
                    overall_xp=data.get("overall_xp", 0.0),
                    xp_to_next=data.get("xp_to_next", 100.0),
                    gravity_theory_level=data.get("gravity_theory_level", 1),
                    gravity_theory_xp=data.get("gravity_theory_xp", 0.0),
                    web_research_level=data.get("web_research_level", 1),
                    web_research_xp=data.get("web_research_xp", 0.0),
                    self_development_level=data.get("self_development_level", 1),
                    self_development_xp=data.get("self_development_xp", 0.0),
                    communication_level=data.get("communication_level", 1),
                    communication_xp=data.get("communication_xp", 0.0),
                    calculation_level=data.get("calculation_level", 1),
                    calculation_xp=data.get("calculation_xp", 0.0),
                    character_growth_level=data.get("character_growth_level", 1),
                    character_growth_xp=data.get("character_growth_xp", 0.0),
                    total_theories=data.get("total_theories", 0),
                    total_researches=data.get("total_researches", 0),
                    total_websites_scanned=data.get("total_websites_scanned", 0),
                    total_messages_sent=data.get("total_messages_sent", 0),
                    total_messages_received=data.get("total_messages_received", 0),
                    total_reports_written=data.get("total_reports_written", 0),
                    total_character_upgrades=data.get("total_character_upgrades", 0),
                    uptime_hours=data.get("uptime_hours", 0.0),
                    level_history=data.get("level_history", []),
                )
        return KnowledgeLevel()

    def _save_events(self):
        """Сохранение событий."""
        path = self.config.state_dir / "events.json"
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([e.to_dict() for e in self.events[-500:]], f, ensure_ascii=False, indent=2)

    def _load_events(self) -> list:
        """Загрузка событий."""
        path = self.config.state_dir / "events.json"
        if path.exists():
            import json
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                events = []
                from datetime import datetime
                for d in data:
                    events.append(HanakoEvent(
                        event_type=d["event_type"],
                        content=d["content"],
                        timestamp=datetime.fromisoformat(d["timestamp"]),
                        metadata=d.get("metadata", {}),
                        event_id=d.get("event_id", ""),
                    ))
                return events
        return []

    # ==================== Статус ====================

    def get_status(self) -> dict:
        """Получить текущий статус."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "running": self.running,
            "cycles": self.total_cycles,
            "level": self.level.to_dict(),
            "theories_count": len(self.theories),
            "research_tasks_count": len(self.research_tasks),
            "messages_count": len(self.messages),
            "reports_count": len(self.reports_list),
            "events_count": len(self.events),
            "character": self.character.get_traits().to_dict(),
            "config": self.config.to_dict(),
        }

    def get_summary(self) -> str:
        """Текстовое резюме статуса."""
        status = self.get_status()
        level = status["level"]
        lines = [
            "=" * 60,
            "🌸 ХАНАКО — Исследователь гравитации",
            "=" * 60,
            f"  Версия: {status['version']}",
            f"  Статус: {'🟢 Работает' if status['running'] else '🔴 Остановлена'}",
            f"  Циклов: {status['cycles']}",
            "",
            "  ─── Уровень знаний ───",
            f"  Общий уровень: {level['overall_level']} ({level['level_name']})",
            f"  Опыт: {level['overall_xp']:.0f}/{level['xp_to_next']:.0f}",
            "",
            "  ─── Специализации ───",
            f"  📐 Теории гравитации: уровень {level['gravity_theory_level']}",
            f"  🌐 Веб-исследования: уровень {level['web_research_level']}",
            f"  🧠 Саморазвитие: уровень {level['self_development_level']}",
            f"  💬 Общение: уровень {level['communication_level']}",
            f"  📊 Вычисления: уровень {level['calculation_level']}",
            f"  🌱 Характер: уровень {level['character_growth_level']}",
            "",
            "  ─── Статистика ───",
            f"  Теорий создано: {level['total_theories']}",
            f"  Исследований: {level['total_researches']}",
            f"  Сайтов просканировано: {level['total_websites_scanned']}",
            f"  Сообщений отправлено: {level['total_messages_sent']}",
            f"  Сообщений получено: {level['total_messages_received']}",
            f"  Отчётов написано: {level['total_reports_written']}",
            f"  Улучшений характера: {level['total_character_upgrades']}",
            "",
            "  ─── Характер ───",
            f"  Темперамент: {status['character']['temperament']}",
            f"  Социальность: {status['character']['sociality']}",
            f"  Мировоззрение: {status['character']['worldview']}",
            "",
            "=" * 60,
        ]
        return "\n".join(lines)

    # ================================================================
    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # ================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"🌌 [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
        self.logger.info(f"💬 Ханако пишет {target}: {human_msg[:100]}...")
        
        if self.config.communication_enabled:
            try:
                msg = ScientistMessage(
                    sender="hanako",
                    recipient=target,
                    content=human_msg,
                    message_type=CommunicationType.DISCUSSION,
                )
                msg.message_id = f"hanako_humanity_{uuid.uuid4().hex[:8]}"
                self.communication.send_message(msg)
                self.level.total_messages_sent += 1
                
                self.humanity.memory.record_sister_chat(
                    target, topic,
                    self.humanity.mood.current_mood,
                    self.humanity.mood.current_mood
                )
            except Exception as e:
                self.logger.warning(f"Не удалось отправить сообщение: {e}")
