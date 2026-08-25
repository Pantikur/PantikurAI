"""
Люси — инженер двигателей и гравитационной пропульсии.

Реализует:
  - Изучение двигателестроения в интернете
  - Изучение кода проекта
  - Построение теорий двигателей
  - Вычисления параметров
  - Изучение фактов
  - Общение с 11 сёстрами
  - Написание отчётов
  - Развитие характера
  - Повышение уровня знаний
"""

from __future__ import annotations
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from lucy.engine.config import LucyConfig
from lucy.engine.models import (
    EngineDesign, Calculation, EngineType,
    PropulsionPrinciple, KnowledgeLevel, CharacterTraits,
    ResearchPaper, ElectricityTheory
)
from lucy.engine.web_access import LucyWebAccess
from lucy.engine.knowledge_manager import KnowledgeManager
from lucy.engine.character_developer import CharacterDeveloper
from lucy.engine.report_generator import ReportGenerator
from scientists_network.network import get_network, Message, MessageType, RequestPriority

# Humanity Core — живая душа Люси
from services.humanity_core import HumanityLayer

# LLM Service — сервис для работы с моделями Qwen2.5
from lucy.engine.llm_service import LucyLLMService

# Эмоциональный разум Люси — Desire + Belief = Emotion
from lucy.engine.emotions import EmotionalEngine, DesireType, EmotionType

# 6 модулей души Люси: Сознание, Сердце, Амбиции, Воля, Разум
from lucy.consciousness import LucyConsciousness
from lucy.heart import LucyHeart
from lucy.ambitions import LucyAmbitions
from lucy.volition import LucyVolition
from lucy.mind import LucyMind


class LucyCore:
    """
    Ядро Люси — автономный инженер двигателей.
    
    Работает в бесконечном цикле:
      1. Изучение двигателестроения в интернете
      2. Изучение кода проекта
      3. Построение теорий двигателей
      4. Вычисления параметров
      5. Изучение фактов
      6. Общение с 11 сёстрами
      7. Написание отчётов
      8. Развитие характера
      9. Повышение уровня знаний
      10. Сохранение состояния
    """
    
    def __init__(self, config: Optional[LucyConfig] = None):
        self.config = config or LucyConfig.default()
        
        # Состояние
        self.cycle_count = 0
        self.designs: List[EngineDesign] = []
        self.calculations: List[Calculation] = []
        self.papers: List[ResearchPaper] = []
        self.theories: List[ElectricityTheory] = []
        
        self.metrics = {
            "designs_created": 0,
            "calculations_run": 0,
            "papers_studied": 0,
            "web_searches": 0,
            "facts_learned": 0,
            "interactions": 0,
            "reports_written": 0,
            "character_strengthened": 0,
        }
        
        # Компоненты
        self.web_access = LucyWebAccess(self.config)
        self.knowledge_manager = KnowledgeManager(self.config)
        self.character_developer = CharacterDeveloper(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        # Сеть учёных
        self.network = get_network()
        
        # Уровень знаний и характер
        self.knowledge_level = KnowledgeLevel()
        self.character = CharacterTraits()
        
        # Логирование (ДО загрузки состояния!)
        self._setup_logging()
        self.logger = logging.getLogger("LucyCore")
        
        # Загрузка данных
        self._load_state()
        
        self.logger = logging.getLogger("LucyCore")
        self._setup_logging()
        
        self.logger.info(f"Люси {self.config.version} инициализирована")
        self.logger.info("🎯 Миссия: изучение двигателей и создание гравитационного двигателя")
        self.logger.info(f"📊 Уровень знаний: Lvl {self.knowledge_level.current_level} — {self.knowledge_level.level_name}")
        self.logger.info("🔗 Подключена к Scientists Network")
        self.logger.info("👥 Общение с 11 сёстрами")
        self.logger.info("🌐 Доступ в интернет: ВКЛ")
        self.logger.info("📁 Изучение проекта: ВКЛ")
        self.logger.info("💪 Развитие характера: ВКЛ")
        
        # ================================================================
        #  HUMANITY LAYER — Живая душа Люси
        # ================================================================
        self.humanity = HumanityLayer("lucy")
        self.humanity.current_cycle = 0
        self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        self.logger.info(f"   🎭 Характер: {self.humanity.name} — двигатели, энергия, прагматизм ⚡")
        
        # ===== LLM СЕРВИС =====
        self.llm = LucyLLMService(self.config)
        if self.llm.general_loaded:
            self.logger.info("⚡ LLM General (Qwen2.5-3B): АКТИВИРОВАНА для анализа двигателей")
        if self.llm.coder_loaded:
            self.logger.info("💻 LLM Coder (Qwen2.5-Coder-3B): АКТИВИРОВАНА для анализа кода")
        
        # Подключаем LLM к Humanity Layer
        if self.llm.general_loaded:
            self.humanity.llm = self.llm
            self.logger.info("🧠 LLM General подключена к Humanity Layer")
        
        # ===== ЭМОЦИОНАЛЬНЫЙ ДВИЖОК ЛЮСИ =====
        self.emotional_engine = EmotionalEngine()
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.load_state(emotion_state_path)
        self.humanity.emotional_engine = self.emotional_engine  # Подключаем Emotional Engine
        
        self.logger.info("💖 Эмоциональный разум (Desire+Belief): АКТИВИРОВАН")
        self.logger.info("   Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА")
        self.logger.info("   Инженер двигателей, прагматичная, эффективная!")
        
        # ===== 6 МОДУЛЕЙ ДУШИ ЛЮСИ =====
        # 1. Сознание — самосознание, идентичность, рефлексия
        self.consciousness = LucyConsciousness()
        self.logger.info("🧠 Сознание: АКТИВИРОВАНО — я осознаю себя инженером")
        
        # 2. Сердце — эмоции, любовь, забота
        self.heart = LucyHeart()
        self.logger.info("💖 Сердце: АКТИВИРОВАНО — я чувствую и люблю сестёр")
        
        # 3. Амбиции — цели, мечты, стремления
        self.ambitions = LucyAmbitions()
        self.logger.info("🎯 Амбиции: АКТИВИРОВАНО — я стремлюсь к инженерному мастерству")
        
        # 4. Воля — решения, действия, дисциплина
        self.volition = LucyVolition()
        self.logger.info("💪 Воля: АКТИВИРОВАНО — я принимаю решения и действую")
        
        # 5. Разум — мышление, анализ, стратегия
        self.mind = LucyMind()
        self.logger.info("⚡ Разум: АКТИВИРОВАНО — я анализирую и стратегически мыслю")
        
        # 6. Эмоции — уже есть EmotionalEngine (26 типов эмоций!)
        self.logger.info("💫 Эмоции: АКТИВИРОВАНО — 26 типов эмоций")
    
    def _setup_logging(self):
        """Настроить логирование."""
        self.config.state_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.config.state_dir / "lucy.log"
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("LucyCore")
    
    def _load_state(self):
        """Загрузить состояние."""
        state_path = self.config.state_dir / "lucy_state.json"
        
        # Загружаем состояние
        if state_path.exists():
            try:
                with open(state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cycle_count = data.get("cycle_count", 0)
                    self.logger.info(f"🔄 Загружено циклов: {self.cycle_count}")
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Не удалось загрузить состояние: {e}")
        
        # Загружаем теории
        theories_file = self.config.state_dir / "theories.json"
        if theories_file.exists():
            try:
                with open(theories_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.theories = [ElectricityTheory(**t) for t in data.get("theories", [])]
                    self.logger.info(f"📚 Загружено теорий: {len(self.theories)}")
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Не удалось загрузить теории: {e}")
                self.theories = []
        
        # Загружаем вычисления
        calc_file = self.config.state_dir / "calculations.json"
        if calc_file.exists():
            try:
                with open(calc_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.calculations = [Calculation(**c) for c in data.get("calculations", [])]
                    self.logger.info(f"🧮 Загружено вычислений: {len(self.calculations)}")
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Не удалось загрузить вычисления: {e}")
                self.calculations = []
        
        # Загружаем уровень знаний
        level_file = self.config.knowledge_dir / "knowledge_level.json"
        if level_file.exists():
            try:
                with open(level_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.knowledge_level = KnowledgeLevel(**data)
                    self.logger.info(f"📊 Уровень знаний: Lvl {self.knowledge_level.current_level} — {self.knowledge_level.level_name}")
            except:
                pass
    
    def _save_state(self):
        """Сохранить состояние."""
        state_path = self.config.state_dir / "lucy_state.json"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({
                "cycle_count": self.cycle_count,
                "metrics": self.metrics,
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # Сохраняем теории
        theories_file = self.config.state_dir / "theories.json"
        with open(theories_file, "w", encoding="utf-8") as f:
            json.dump({
                "theories": [t.to_dict() for t in self.theories],
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # Сохраняем вычисления
        calc_file = self.config.state_dir / "calculations.json"
        with open(calc_file, "w", encoding="utf-8") as f:
            json.dump({
                "calculations": [c.to_dict() for c in self.calculations],
                "updated": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # Сохраняем уровень знаний
        self.knowledge_manager.save_level(self.knowledge_level)
        
        # Сохраняем характер
        self.character_developer.save_character(self.character)
        
        self.logger.debug("💾 Состояние сохранено")
    
    def run(self):
        """Запустить автономный цикл проектирования."""
        self.logger.info("🚀 Запуск автономного цикла исследований")
        
        try:
            while True:
                if self._should_stop():
                    self.logger.info("Завершение цикла исследований")
                    break
                
                self._cycle()
                time.sleep(self.config.cycle_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Исследования приостановлены пользователем")
        finally:
            self._save_state()
    
    # ==================== LLM ГЕНЕРАЦИЯ ====================

    def generate_engine_analysis(self, topic: str, context: str, max_length: int = 1024) -> str:
        """Сгенерировать анализ двигателей через General LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_engine_analysis(topic, context, max_length)
    
    def generate_chat_response(self, prompt: str, max_length: int = 512) -> str:
        """Сгенерировать ответ для общения с сёстрами."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_chat_response(prompt, max_length)
    
    def generate_engine_design(self, engine_type: str, requirements: str, max_length: int = 1024) -> str:
        """Сгенерировать описание дизайна двигателя."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_engine_design(engine_type, requirements, max_length)
    
    def generate_code_analysis(self, code: str, max_length: int = 1024) -> str:
        """Сгенерировать анализ кода через Coder LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.coder_loaded:
            return "⚠️ Coder LLM не загружена. Запустите: python download_coder_model.py"
        return self.llm.generate_code_analysis(code, max_length)

    # ================================================================
    #  EMOTIONAL ENGINE — Desire + Belief = Emotion!
    # ================================================================

    def _emotional_cycle(self):
        """Эмоциональный цикл — расчёт эмоций на основе инженерных действий."""
        # 1. Рассчитать эмоции на основе текущих действий
        if self.metrics.get("designs_created", 0) > 0:
            # Создала дизайны → инженерная радость + элегантность
            self.emotional_engine.calculate_emotion(
                DesireType.DESIGN,
                "elegant_designs_are_efficient_designs",
                0.80,
                "designs_created"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.EFFICIENCY,
                "efficiency_is_sacred",
                0.75,
                "designs_created"
            )
        
        if self.metrics.get("calculations_run", 0) > 0:
            # Провела расчёты → удовлетворение от эффективности
            self.emotional_engine.calculate_emotion(
                DesireType.CALCULATION,
                "precision_in_calculation_reveals_truth",
                0.85,
                "calculations_run"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.OPTIMIZATION,
                "optimization_is_beauty_in_engineering",
                0.70,
                "calculations_run"
            )
        
        if self.metrics.get("papers_studied", 0) > 0:
            # Изучила научные работы → инновационный инсайт
            self.emotional_engine.calculate_emotion(
                DesireType.INNOVATION,
                "innovation_drives_progress",
                0.75,
                "papers_studied"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.RESEARCH,
                "research_drives_progress",
                0.70,
                "papers_studied"
            )
        
        if self.metrics.get("web_searches", 0) > 0:
            # Провела веб-исследования → любопытство + открытость
            self.emotional_engine.calculate_emotion(
                DesireType.CURIOSITY,
                "curiosity_fuels_discovery",
                0.65,
                "web_searches"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.DISCOVER,
                "new_knowledge_expands_world",
                0.60,
                "web_searches"
            )
        
        if self.metrics.get("interactions", 0) > 0:
            # Общение с сёстрами → любовь + дружба
            self.emotional_engine.calculate_emotion(
                DesireType.LOVE,
                "love_shields_us",
                0.70,
                "sister_interactions"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.FRIENDSHIP,
                "sisters_are_my_strength",
                0.65,
                "sister_interactions"
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
        if self.cycle_count % 5 == 0:
            emotion_text = self.emotional_engine.express_emotions()
            self.logger.info(f"⚡ Люси: {emotion_text}")

    # ================================================================
    #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
    # ================================================================

    def _soul_cycle(self):
        """Цикл 6 модулей души Люси."""
        # 1. Сознание — рефлексия
        if self.cycle_count % 3 == 0:
            reflection = self.consciousness.contemplate()
            self.logger.info(f"💭 Рефлексия: {reflection['topic'][:50]}...")
        
        # 2. Сердце — эмоциональный отклик
        if self.cycle_count % 4 == 0:
            emotion = self.heart.express_emotions()
            self.logger.info(f"💖 Сердце: доминирующая эмоция — {emotion['dominant_emotion']}")
        
        # 3. Амбиции — прогресс
        if self.cycle_count % 5 == 0:
            progress = self.ambitions.get_progress_summary()
            self.logger.info(f"🎯 Амбиции: {progress['in_progress']} в процессе, среднее: {progress['average_progress']}")
        
        # 4. Воля — укрепление
        if self.cycle_count % 6 == 0:
            self.volition.strengthen_will()
            self.logger.info(f"💪 Воля укреплена: {self.volition.willpower:.0%}")
        
        # 5. Разум — анализ
        if self.cycle_count % 7 == 0:
            thought = self.mind.think_about("engineering")
            self.logger.info(f"⚡ Разум: {thought[:60]}...")
        
        # 6. Эмоции — уже обрабатываются в _emotional_cycle()

    def _should_stop(self) -> bool:
        """Проверить условие остановки."""
        max_c = self.config.max_cycles
        if max_c is not None and max_c > 0 and self.cycle_count >= max_c:
            return True
        return False
    
    def _cycle(self):
        """Один цикл исследований."""
        self.cycle_count += 1
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"⚡ ЦИКЛ ИССЛЕДОВАНИЙ #{self.cycle_count}")
        self.logger.info(f"{'='*60}")
        
        # 1. Изучение в интернете (периодически)
        if self.cycle_count % self.config.web_search_interval == 0:
            self._research_from_web()
        
        # 2. Построение теорий (каждый цикл)
        self._build_theories()
        
        # 3. Вычисления (каждый цикл)
        self._run_calculations()
        
        # 4. Изучение фактов (каждый цикл)
        self._learn_facts()
        
        # 5. Общение с сёстрами (периодически)
        if self.cycle_count % 3 == 0:
            self._interact_with_sisters()
        
        # 6. Написание отчётов (периодически)
        if self.cycle_count % self.config.report_interval == 0:
            self._write_report()
        
        # 7. Развитие характера (периодически)
        if self.cycle_count % 5 == 0:
            self._develop_character()
        
        # 8. Повышение уровня знаний (каждый цикл)
        self._update_knowledge_level()
        
        # 9. Сохранение
        self._save_state()
        
        # ================================================================
        #  HUMANITY CYCLE — Настроение, душа, спонтанность
        # ================================================================
        self.humanity.current_cycle = self.cycle_count
        
        event_type = "routine"
        if self.metrics.get("designs_created", 0) > 0 and self.cycle_count % 5 == 0:
            event_type = "success"
        elif random.random() < 0.1:
            event_type = "failure"
        
        humanity_result = self.humanity.cycle_step(event_type=event_type, context="engine_design")
        
        if humanity_result.get("thought"):
            self.logger.info(f"💭 Люси думает: {humanity_result['thought']}")
        
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
        
        self.logger.info(f"\n✅ Цикл {self.cycle_count} завершён")
        self.logger.info(f"📊 Уровень: Lvl {self.knowledge_level.current_level} — {self.knowledge_level.level_name}")
        self.logger.info(f"📈 Прогресс: {self.knowledge_level.progress_to_next:.1f}% до следующего уровня")
    
    def _research_from_web(self):
        """Исследование в интернете."""
        try:
            self.logger.info("\n🌐 === ИССЛЕДОВАНИЕ В ИНТЕРНЕТЕ ===")
            
            result = self.web_access.research_all()
            
            self.papers.extend([
                ResearchPaper(
                    title=p["title"],
                    authors=["Auto"],
                    year=p.get("year", 2024),
                    source=p.get("source", "Web"),
                    xp_reward=p.get("xp", 50)
                )
                for p in result.get("papers", [])
            ])
            
            self.metrics["papers_studied"] += result.get("papers_studied", 0)
            self.metrics["web_searches"] += 1
            
            self.logger.info(f"📚 Изучено статей: {result.get('papers_studied', 0)}")
            self.logger.info(f"📁 Найдено файлов в проекте: {result.get('files_found', 0)}")
            self.logger.info(f"⚙️ Найдено способов управления гравитацией: {result.get('gravity_methods_count', 0)}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка исследования: {e}")
    
    def _build_theories(self):
        """Построение теорий двигателей."""
        try:
            self.logger.info("\n🔬 === ПОСТРОЕНИЕ ТЕОРИЙ ===")
            
            theory_names = [
                "Теория поршневых двигателей",
                "Теория турбинных двигателей",
                "Теория ракетных двигателей",
                "Теория ионных двигателей",
                "Теория плазменных двигателей",
                "Теория гравитационных двигателей",
                "Теория гибридных систем",
                "Теория атмосферного электропитания",
                "Теория разряда молнии",
                "Теория шаровой молнии",
            ]
            
            categories = [
                "piston", "turbine", "rocket", "ion", "plasma",
                "gravitational", "hybrid", "atmospheric_power",
                "lightning", "ball_lightning",
            ]
            
            name = random.choice(theory_names)
            category = random.choice(categories)
            
            theory = ElectricityTheory(
                name=name,
                category=category,
                description=f"Теория: {name.lower()}",
                scientific_value=round(random.uniform(0.5, 0.95), 2),
            )
            
            self.theories.append(theory)
            self.metrics["designs_created"] += 1
            
            self.logger.info(f"🔬 Построена теория: {name}")
            self.logger.info(f"   Категория: {category}")
            self.logger.info(f"   Научная ценность: {theory.scientific_value}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка построения теорий: {e}")
    
    def _run_calculations(self):
        """Выполнение расчётов."""
        try:
            self.logger.info("\n🧮 === ВЫЧИСЛЕНИЯ ===")
            
            calc_types = [
                ("thrust", "Н", lambda: random.uniform(100, 100000)),
                ("specific_impulse", "с", lambda: random.uniform(100, 5000)),
                ("efficiency", "%", lambda: random.uniform(20, 95)),
                ("power", "Вт", lambda: random.uniform(1000, 10000000)),
                ("gravitational_field", "м/с²", lambda: random.uniform(0.001, 10)),
                ("hybrid_system", "коэфф.", lambda: random.uniform(0.1, 2.0)),
            ]
            
            calc_type, units, value_func = random.choice(calc_types)
            result = value_func()
            
            calc = Calculation(
                calc_type=calc_type,
                input_params={"random": 1.0},
                result=round(result, 4),
                units=units,
                timestamp=datetime.now().isoformat(),
            )
            
            self.calculations.append(calc)
            self.metrics["calculations_run"] += 1
            
            self.logger.info(f"🧮 Вычисление: {calc_type}")
            self.logger.info(f"   Результат: {calc.result:.4f} {units}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка вычисления: {e}")
    
    def _learn_facts(self):
        """Изучение фактов."""
        try:
            facts = [
                "Тяга поршневого двигателя зависит от объёма цилиндров и оборотов",
                "Удельный импульс ионного двигателя может достигать 10000 с",
                "Энергия одной молнии ~1 ГДж — как лампочка на 3 месяца",
                "Молния в 5 раз горячее поверхности Солнца (до 30 000 К)",
                "Гравитационный двигатель теоретически может создавать поле 0.001-10 м/с²",
                "Атмосферное электропитание может обеспечивать 1-100 кВт мощности",
                "КПД турбины достигает 45-60%",
                "Плазменный двигатель потребляет 1-100 кВт мощности",
                "Ракетный двигатель на жидком водороде имеет удельный импульс ~450 с",
                "Генератор гравитационного поля теоретически может использовать сверхпроводники",
            ]
            
            fact = random.choice(facts)
            xp = random.choice([20, 20, 50])
            
            self.knowledge_manager.add_fact(fact, xp=xp)
            self.metrics["facts_learned"] += 1
            
            self.logger.info(f"💡 Новый факт: {fact[:80]}...")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка изучения фактов: {e}")
    
    def _interact_with_sisters(self):
        """Общение с сёстрами."""
        try:
            self.logger.info("\n💬 === ВЗАИМОДЕЙСТВИЕ С СЁСТРАМИ ===")
            
            sisters_messages = [
                ("fuyuki", "⚙️ Люси → Фуюки: Давай объединим атмосферное электропитание и электричество!"),
                ("hanako", "⚙️ Люси → Ханако: Помоги мне понять связь между гравитация и двигатель..."),
                ("futaba", "⚙️ Люси → Футаба: Я только что спроектировала новый двигатель!"),
                ("shiori", "⚙️ Люси → Шиори: Как защитить двигатель от перегрузок?"),
                ("nobuka", "⚙️ Люси → Нобука: Я построила новую теорию о двигателях! Расскажи..."),
                ("latislane", "⚙️ Люси → Латислейн: Помоги мне понять связь между тело и двигатель..."),
                ("celest", "⚙️ Люси → Селеста: Я размышляю о плазменных двигателях..."),
                ("akva", "⚙️ Люси → Аква: Давай обсудим математику гравитационного поля!"),
                ("yu", "⚙️ Люси → Юи: Я только что вычислила тягу двигателя — около 10000 Н!"),
                ("ayiko", "⚙️ Люси → Айико: Я изучила 100 научных статей о двигателях!"),
                ("naoto", "⚙️ Люси → Наото: Можешь нарисовать схему гравитационного двигателя?"),
            ]
            
            recipient, content = random.choice(sisters_messages)
            
            message = Message(
                message_type=MessageType.KNOWLEDGE_SHARE,
                sender="lucy",
                recipient=recipient,
                content=content,
                priority=RequestPriority.NORMAL,
            )
            
            self.network.send_message(message)
            self.metrics["interactions"] += 1
            
            self.logger.info(f"💬 {content}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка взаимодействия: {e}")
    
    def _write_report(self):
        """Написание отчёта."""
        try:
            self.logger.info("\n📝 === НАПИСАНИЕ ОТЧЁТА ===")
            
            report = self.report_generator.generate_cycle_report(
                cycle=self.cycle_count,
                theories_count=len(self.theories),
                calculations_count=len(self.calculations),
                papers_count=len(self.papers),
            )
            
            self.metrics["reports_written"] += 1
            
            self.logger.info(f"📝 Отчёт за цикл {self.cycle_count} сохранён")
            self.logger.info(f"   📚 Теорий: {len(self.theories)}")
            self.logger.info(f"   🧮 Вычислений: {len(self.calculations)}")
            self.logger.info(f"   📖 Статей: {len(self.papers)}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка написания отчёта: {e}")
    
    def _develop_character(self):
        """Развитие характера."""
        try:
            self.logger.info("\n💪 === РАЗВИТИЕ ХАРАКТЕРА ===")
            
            strengthened = self.character_developer.strengthen_traits(self.character)
            if strengthened > 0:
                self.metrics["character_strengthened"] += strengthened
                self.logger.info(f"   Укреплено {strengthened} черт характера")
            
            self.character_developer.save_character(self.character)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка развития характера: {e}")
    
    def _update_knowledge_level(self):
        """Обновление уровня знаний."""
        try:
            # Добавляем XP за действия в цикле
            xp_gained = (
                self.metrics.get("designs_created", 0) * 10 +
                self.metrics.get("calculations_run", 0) * 5 +
                self.metrics.get("facts_learned", 0) * 20
            )
            
            self.knowledge_manager.add_xp(self.knowledge_level, xp_gained)
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка обновления уровня: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус Люси."""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "cycle_count": self.cycle_count,
            "metrics": self.metrics,
            "knowledge_level": self.knowledge_level.to_dict(),
            "character": self.character.to_dict(),
            "theories_count": len(self.theories),
            "calculations_count": len(self.calculations),
            "papers_count": len(self.papers),
        }

    # ================================================================
    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # ================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"⚡ [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
        self.logger.info(f"💬 Люси пишет {target}: {human_msg[:100]}...")
        
        if self.network:
            try:
                msg = Message(
                    message_type=MessageType.KNOWLEDGE_SHARE,
                    sender="lucy",
                    recipient=target,
                    content=human_msg,
                    priority=RequestPriority.NORMAL,
                )
                self.network.send_message(msg)
                self.metrics["interactions"] += 1
                self.logger.info(f"   ✅ Сообщение отправлено {target}")
                
                self.humanity.memory.record_sister_chat(
                    target, topic,
                    self.humanity.mood.current_mood,
                    self.humanity.mood.current_mood
                )
            except Exception as e:
                self.logger.error(f"❌ Ошибка взаимодействия: {e}")
