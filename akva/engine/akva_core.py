"""
Аква — Ядро научного модуля Pantikur.

Изучает: математика, физика, аэродинамика, сопротивление материалов.
Функции: саморазвитие, интернет, автономная работа, общение, отчёты, характер.
"""

from scientists_network.character_system import CharacterSystem
import json
import logging
import math
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import AkvaConfig
from .models import (
    AkvaCalculation, AkvaTheory, Constitution, KnowledgeLevel,
    Message, PersonalityVector, XP_TABLE, ResearchArea,
)
from .web_access import AkvaWebAccess
from .reporter import AkvaReporter
from .communicator import AkvaCommunicator

# Humanity Core — живая душа Аква
from humanity_core import HumanityLayer

# LLM Service — сервис для работы с моделями Qwen2.5
from akva.engine.llm_service import AkvaLLMService

# Эмоциональный разум Аква — Desire + Belief = Emotion
from akva.engine.emotions import EmotionalEngine, DesireType, EmotionType

# 6 модулей души Аква: Сознание, Сердце, Амбиции, Воля, Разум
from akva.consciousness import AkvaConsciousness
from akva.heart import AkvaHeart
from akva.ambitions import AkvaAmbitions
from akva.volition import AkvaVolition
from akva.mind import AkvaMind


logger = logging.getLogger("AkvaCore")


# =====================================================================
#  ТЕМЫ ИССЛЕДОВАНИЙ
# =====================================================================

THEME_TEMPLATES = {
    "mathematics": {
        "simple": [
            "Интегральное исчисление", "Линейные уравнения",
            "Матрицы и определители", "Пределы и ряды",
            "Тригонометрия", "Комбинаторика",
        ],
        "complex": [
            "Уравнения Навье-Стокса", "Теория чисел",
            "Топология многообразий", "Функциональный анализ",
            "Теория категорий", "Дифференциальная геометрия",
            "Теория вероятностей стохастических процессов",
            "Оптимизация невыпуклых функций",
            "Метод Монте-Карло", "Численные методы",
        ],
    },
    "physics": {
        "simple": [
            "Законы Ньютона", "Термодинамика базовая",
            "Электромагнетизм", "Оптика",
            "Механика твердого тела", "Звук и волны",
        ],
        "complex": [
            "Квантовая механика многотельных систем",
            "Термодинамика неравновесных процессов",
            "Квантовая запутанность", "Гравитационные волны",
            "Относительность и гравитация", "Плазменная физика",
            "Квантовая электродинамика", "Физика элементарных частиц",
        ],
    },
    "aerodynamics": {
        "simple": [
            "Подъёмная сила крыла", "Сопротивление воздуха",
            "Число Маха", "Уравнение Бернулли",
        ],
        "complex": [
            "Турбулентность и пограничный слой",
            "Ударные волны сверхзвукового обтекания",
            "Подъёмная сила крыла сложной формы",
            "Компьютерная гидродинамика (CFD)",
            "Аэродинамика микролетательных аппаратов",
            "Аэроупругость",
        ],
    },
    "strength_of_materials": {
        "simple": [
            "Прочность при растяжении", "Модуль Юнга",
            "Напряжение и деформация", "Момент инерции",
        ],
        "complex": [
            "Усталость материалов при циклических нагрузках",
            "Механика разрушения трещин",
            "Прочность композитных материалов",
            "Критерии прочности (Треска, фон Мизес)",
            "Ползучесть материалов при высоких температурах",
            "Анализ напряжений методом конечных элементов",
        ],
    },
}


# =====================================================================
#  ФОРМУЛЫ И ВЫЧИСЛЕНИЯ
# =====================================================================

CALC_TEMPLATES = {
    "mathematics": [
        ("Интеграл Римана", lambda: round(random.uniform(1.0, 1000.0), 4), "∫f(x)dx", ""),
        ("Собственные значения матрицы", lambda: round(random.uniform(0.1, 100.0), 4), "Ax=λx", ""),
        ("Решение системы уравнений", lambda: round(random.uniform(0.001, 10000.0), 6), "AX=B", ""),
        ("Вероятность события", lambda: round(random.uniform(0.0, 1.0), 4), "P(A)", ""),
        ("Ряд Тейлора", lambda: round(random.uniform(0.0001, 100.0), 6), "Σ f⁽ⁿ⁾(a)/n! * (x-a)ⁿ", ""),
        ("Дифференциальное уравнение", lambda: round(random.uniform(-1000.0, 1000.0), 4), "dy/dx = f(x,y)", ""),
    ],
    "physics": [
        ("Сила тяготения", lambda: round(random.uniform(0.1, 1e10), 2), "F=G*m1*m2/r²", "N"),
        ("Энергия частицы", lambda: round(random.uniform(0.01, 1e15), 2), "E=mc²", "J"),
        ("Температура равновесия", lambda: round(random.uniform(100.0, 5000.0), 2), "T=Q/mc", "K"),
        ("Частота колебаний", lambda: round(random.uniform(0.1, 1e9), 2), "f=1/T", "Hz"),
        ("Скорость волны", lambda: round(random.uniform(1.0, 3e8), 2), "v=λf", "m/s"),
        ("Импульс частицы", lambda: round(random.uniform(0.01, 1e8), 4), "p=mv", "kg·m/s"),
    ],
    "aerodynamics": [
        ("Подъёмная сила", lambda: round(random.uniform(10.0, 1e7), 2), "L=Cl×0.5×ρ×v²×S", "N"),
        ("Сила сопротивления", lambda: round(random.uniform(1.0, 1e6), 2), "D=Cd×0.5×ρ×v²×S", "N"),
        ("Число Рейнольдса", lambda: round(random.uniform(100.0, 1e8), 2), "Re=ρ×v×L/μ", ""),
        ("Скорость звука", lambda: round(random.uniform(200.0, 1200.0), 2), "a=√(γ×R×T)", "m/s"),
        ("Критическое число Маха", lambda: round(random.uniform(0.5, 1.5), 4), "M_crit", ""),
        ("Подъёмное отношение", lambda: round(random.uniform(5.0, 30.0), 2), "L/D", ""),
    ],
    "strength_of_materials": [
        ("Предел прочности", lambda: round(random.uniform(10.0, 2000.0), 2), "σ=F/A", "MPa"),
        ("Модуль Юнга", lambda: round(random.uniform(1.0, 400.0), 2), "E=σ/ε", "GPa"),
        ("Момент инерции", lambda: round(random.uniform(0.001, 100.0), 6), "I=∫y²dA", "m⁴"),
        ("Коэффициент запаса", lambda: round(random.uniform(1.0, 10.0), 2), "n=σ_пред/σ_раб", ""),
        ("Деформация материала", lambda: round(random.uniform(0.0001, 0.5), 6), "ε=ΔL/L", ""),
        ("Критическая нагрузка Эйлера", lambda: round(random.uniform(1000.0, 1e9), 2), "P_cr=π²×E×I/(K×L)²", "N"),
    ],
}


THEORY_TEMPLATES = {
    "mathematics": [
        ("Обобщённое дифференциальное уравнение", "differential", 0.85),
        ("Теория чисел и криптография", "number_theory", 0.78),
        ("Линейная алгебра многомерных пространств", "linear_algebra", 0.82),
        ("Теория вероятностей стохастических процессов", "probability", 0.75),
        ("Оптимизация невыпуклых функций", "optimization", 0.88),
        ("Топологический анализ данных", "topology", 0.80),
    ],
    "physics": [
        ("Квантовая механика многотельных систем", "quantum", 0.90),
        ("Термодинамика неравновесных процессов", "thermodynamics", 0.83),
        ("Электромагнитная теория поля", "electromagnetism", 0.86),
        ("Относительность и гравитация", "relativity", 0.92),
        ("Механика сплошных сред", "mechanics", 0.80),
        ("Квантовая запутанность и информация", "quantum_info", 0.88),
    ],
    "aerodynamics": [
        ("Подъёмная сила крыла сложной формы", "lift", 0.87),
        ("Сопротивление воздуха турбулентного потока", "drag", 0.84),
        ("Ударные волны сверхзвукового обтекания", "shock_waves", 0.91),
        ("Пограничный слой на шероховатой поверхности", "boundary_layer", 0.79),
        ("Турбулентность и переходные явления", "turbulence", 0.86),
        ("Аэроупругость гибких конструкций", "aeroelasticity", 0.82),
    ],
    "strength_of_materials": [
        ("Прочность композитных материалов", "strength", 0.85),
        ("Жёсткость балочных конструкций", "stiffness", 0.80),
        ("Устойчивость сжатых стержней", "stability", 0.83),
        ("Усталость материалов при циклических нагрузках", "fatigue", 0.88),
        ("Механика разрушения трещин", "fracture", 0.90),
        ("Ползучесть при высоких температурах", "creep", 0.84),
    ],
}


class AkvaCore:
    """Основное ядро Аква — научный модуль Pantikur."""

    def __init__(self, config: Optional[AkvaConfig] = None):
        self.config = config or AkvaConfig.default()
        self.current_version = self.config.version

        # Состояние
        self.cycle_count = 0
        self._shutdown_requested = False

        # Персональность (характер)
        self.personality = PersonalityVector()

        # Уровни знаний
        self.knowledge_levels: Dict[str, KnowledgeLevel] = {}
        for area in self.config.research_areas:
            self.knowledge_levels[area] = KnowledgeLevel(area=area)

        # Данные
        self.theories: List[AkvaTheory] = []
        self.calculations: List[AkvaCalculation] = []
        self.research_history: List[Dict[str, Any]] = []

        # Метрики
        self.metrics = {
            "cycles_completed": 0,
            "total_xp": 0,
            "theories_built": 0,
            "calculations_run": 0,
            "web_searches": 0,
            "messages_sent": 0,
            "reports_written": 0,
        }

        # Подмодули
        self.web_access = AkvaWebAccess(self.config)
        self.reporter = AkvaReporter(self.config)
        self.communicator = AkvaCommunicator(self.config)

        # Конституция
        self.constitution = Constitution()

        # Логирование
        self._setup_logging()
        self.logger = logging.getLogger("AkvaCore")

        # Загрузка состояния
        self._load_state()

        self.logger.info(f"Аква {self.current_version} инициализирована")
        self.logger.info(f"Фокус: {', '.join(self.config.research_areas)}")
        self.logger.info(f"Характер: {self.personality.level_description()}")

        # Система характера (общая для всех девочек)
        self.character = CharacterSystem("akva", self.config.state_dir)
        self.logger.info(f"Character loaded: {self.character.get_traits().temperament}")
        
        # ================================================================
        #  HUMANITY LAYER — Живая душа Аква
        # ================================================================
        self.humanity = HumanityLayer("akva")
        self.humanity.current_cycle = 0
        self.logger.info("🧠 Humanity Layer: АКТИВИРОВАН")
        self.logger.info(f"   🎭 Характер: {self.humanity.name} — математика, физика, элегантность 📐")
        
        # ===== LLM СЕРВИС =====
        self.llm = AkvaLLMService(self.config)
        if self.llm.general_loaded:
            self.logger.info("🔬 LLM General (Qwen2.5-3B): АКТИВИРОВАНА для научного анализа")
        if self.llm.coder_loaded:
            self.logger.info("💻 LLM Coder (Qwen2.5-Coder-3B): АКТИВИРОВАНА для анализа кода")
        
        # Подключаем LLM к Humanity Layer
        if self.llm.general_loaded:
            self.humanity.llm = self.llm
            self.logger.info("🧠 LLM General подключена к Humanity Layer")
        
        # ===== ЭМОЦИОНАЛЬНЫЙ ДВИЖОК АКВА =====
        self.emotional_engine = EmotionalEngine()
        emotion_state_path = self.config.state_dir / "emotional_state.json"
        self.emotional_engine.load_state(emotion_state_path)
        self.humanity.emotional_engine = self.emotional_engine  # Подключаем Emotional Engine
        
        self.logger.info("💖 Эмоциональный разум (Desire+Belief): АКТИВИРОВАН")
        self.logger.info("   Формула: ЭМОЦИЯ = ЖЕЛАНИЕ + ВЕРА")
        self.logger.info("   Научный аналитик, исследователь, математик!")

        # ===== 6 МОДУЛЕЙ ДУШИ АКВА =====
        # 1. Сознание — самосознание, идентичность, рефлексия
        self.consciousness = AkvaConsciousness()
        self.logger.info("🧠 Сознание: АКТИВИРОВАНО — я осознаю себя научным аналитиком")
        
        # 2. Сердце — эмоции, любовь, забота
        self.heart = AkvaHeart()
        self.logger.info("💖 Сердце: АКТИВИРОВАНО — я чувствую и люблю сестёр")
        
        # 3. Амбиции — цели, мечты, стремления
        self.ambitions = AkvaAmbitions()
        self.logger.info("🎯 Амбиции: АКТИВИРОВАНО — я стремлюсь к научному мастерству")
        
        # 4. Воля — решения, действия, дисциплина
        self.volition = AkvaVolition()
        self.logger.info("💪 Воля: АКТИВИРОВАНО — я принимаю решения и действую")
        
        # 5. Разум — мышление, анализ, стратегия
        self.mind = AkvaMind()
        self.logger.info("🌟 Разум: АКТИВИРОВАНО — я анализирую и стратегически мыслю")
        
        # 6. Эмоции — уже есть EmotionalEngine (26 типов эмоций!)
        self.logger.info("💫 Эмоции: АКТИВИРОВАНО — 26 типов эмоций")

    def _setup_logging(self):
        log_handler = logging.FileHandler(
            self.config.log_path, encoding='utf-8', mode='a'
        )
        log_handler.setFormatter(logging.Formatter(self.config.log_format))
        file_logger = logging.getLogger("AkvaCore")
        file_logger.addHandler(log_handler)
        file_logger.setLevel(getattr(logging, self.config.log_level, logging.INFO))

    # ================================================================
    #  СОСТОЯНИЕ
    # ================================================================

    def _load_state(self):
        if self.config.state_path.exists():
            try:
                with open(self.config.state_path, "r", encoding="utf-8") as f:
                    state = json.load(f)

                self.metrics.update(state.get("metrics", {}))
                self.cycle_count = state.get("cycle_count", 0)

                if "personality" in state:
                    p = state["personality"]
                    self.personality = PersonalityVector(
                        curiosity=p.get("curiosity", 0.70),
                        precision=p.get("precision", 0.70),
                        patience=p.get("patience", 0.70),
                        creativity=p.get("creativity", 0.70),
                        friendliness=p.get("friendliness", 0.70),
                        confidence=p.get("confidence", 0.70),
                        empathy=p.get("empathy", 0.70),
                    )

                if "knowledge_levels" in state:
                    for area, data in state["knowledge_levels"].items():
                        self.knowledge_levels[area] = KnowledgeLevel(
                            area=area,
                            level=data.get("level", 1),
                            xp=data.get("xp", 0),
                            topics_studied=data.get("topics_studied", []),
                            theories_built=data.get("theories_built", []),
                            calculations_done=data.get("calculations_done", 0),
                        )

                self.logger.info(
                    f"✅ Состояние загружено: циклы={self.cycle_count}, "
                    f"теорий={len(self.theories)}, вычислений={len(self.calculations)}"
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Ошибка загрузки состояния: {e}")
        else:
            self.logger.info("ℹ️ Новое состояние Аква создано")

    def _save_state(self):
        try:
            state = {
                "metrics": self.metrics,
                "cycle_count": self.cycle_count,
                "personality": self.personality.to_dict(),
                "knowledge_levels": {
                    area: kl.to_dict() for area, kl in self.knowledge_levels.items()
                },
                "theories": [t.to_dict() for t in self.theories[-30:]],
                "calculations": [c.to_dict() for c in self.calculations[-30:]],
            }

            self.config.state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            with open(self.config.personality_path, "w", encoding="utf-8") as f:
                json.dump(self.personality.to_dict(), f, ensure_ascii=False, indent=2)

            with open(self.config.knowledge_levels_path, "w", encoding="utf-8") as f:
                json.dump({
                    area: kl.to_dict()
                    for area, kl in self.knowledge_levels.items()
                }, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"❌ Ошибка сохранения состояния: {e}")

    # ================================================================
    #  LLM ГЕНЕРАЦИЯ
    # ================================================================

    def generate_scientific_analysis(self, topic: str, data: str, max_length: int = 1024) -> str:
        """Сгенерировать научный анализ через General LLM."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_scientific_analysis(topic, data, max_length)
    
    def generate_chat_response(self, prompt: str, max_length: int = 512) -> str:
        """Сгенерировать ответ для общения с сёстрами."""
        if not hasattr(self, 'llm') or self.llm is None or not self.llm.general_loaded:
            return "⚠️ LLM не загружена. Запустите: python download_qwen_model.py"
        return self.llm.generate_chat_response(prompt, max_length)
    
    def generate_theory_explanation(self, theory: str, complexity: str = "simple", max_length: int = 1024) -> str:
        """Сгенерировать объяснение теории."""
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
        """Цикл 6 модулей души Аква."""
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
            thought = self.mind.think_about("science")
            self.logger.info(f"🌟 Разум: {thought[:60]}...")
        
        # 6. Эмоции — уже обрабатываются в _emotional_cycle()

    # ================================================================
    #  EMOTIONAL ENGINE — Desire + Belief = Emotion!
    # ================================================================

    def _emotional_cycle(self):
        """Эмоциональный цикл — расчёт эмоций на основе научных действий."""
        # 1. Рассчитать эмоции на основе текущих действий
        if self.metrics.get("calculations_run", 0) > 0:
            # Провела расчёты → поток расчётов + точность
            self.emotional_engine.calculate_emotion(
                DesireType.CALCULATION,
                "precision_matters",
                0.85,
                "calculations_run"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.PRECISION,
                "accuracy_is_essential",
                0.80,
                "calculations_run"
            )
        
        if self.metrics.get("theories_built", 0) > 0:
            # Построила теории → теоретическая элегантность + вдохновение
            self.emotional_engine.calculate_emotion(
                DesireType.THEORY,
                "theories_explain_world",
                0.75,
                "theories_built"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.KNOWLEDGE,
                "science_drives_progress",
                0.70,
                "theories_built"
            )
        
        if self.metrics.get("web_searches", 0) > 0:
            # Провела исследования → любопытство + открытие
            self.emotional_engine.calculate_emotion(
                DesireType.RESEARCH,
                "curiosity_fuels_discovery",
                0.65,
                "web_searches"
            )
            self.emotional_engine.calculate_emotion(
                DesireType.DISCOVERY,
                "new_knowledge_expands_world",
                0.60,
                "web_searches"
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
            self.logger.info(f"🔬 Аква: {emotion_text}")

    # ================================================================
    #  ВЫБОР НАПРАВЛЕНИЯ
    # ================================================================

    def _select_research_area(self) -> str:
        area_levels = {area: kl.level for area, kl in self.knowledge_levels.items()}
        min_level = min(area_levels.values())
        weakest_areas = [area for area, lvl in area_levels.items() if lvl == min_level]

        max_level = max(area_levels.values())
        if max_level - min_level < 10:
            weights = {}
            for area in self.config.research_areas:
                base_weight = 1.0 / (area_levels.get(area, 1) + 1)
                curiosity_boost = self.personality.curiosity * 0.5
                weights[area] = base_weight + curiosity_boost
        else:
            weights = {area: 1.0 for area in weakest_areas}

        areas = list(weights.keys())
        w = list(weights.values())
        return random.choices(areas, weights=w, k=1)[0]

    def _select_topic(self, area: str) -> tuple:
        templates = THEME_TEMPLATES.get(area, THEME_TEMPLATES["mathematics"])
        kl = self.knowledge_levels.get(area)
        level = kl.level if kl else 1
        complexity_chance = 0.3 + (level / 100) * 0.4 + self.personality.creativity * 0.2

        is_complex = random.random() < complexity_chance
        pool = templates["complex"] if is_complex else templates["simple"]
        topic = random.choice(pool)
        return topic, is_complex

    # ================================================================
    #  ИССЛЕДОВАНИЕ
    # ================================================================

    def _study_topic(self, area: str, topic: str, is_complex: bool) -> int:
        xp = XP_TABLE["study_complex"] if is_complex else XP_TABLE["study_simple"]

        kl = self.knowledge_levels.get(area)
        if kl and kl.level > 20:
            xp = int(xp * 1.2)

        changes = {
            "curiosity": 0.02 if is_complex else 0.01,
            "precision": 0.01,
            "patience": 0.01 if is_complex else 0.005,
        }
        self.personality.apply_change(changes)

        if kl:
            kl.add_xp(xp)
            if topic not in kl.topics_studied[-50:]:
                kl.topics_studied.append(topic)

        self.logger.info(f"📚 Изучено: {area} — {topic} ({'сложно' if is_complex else 'базово'}) | +{xp} XP")
        return xp

    def _web_research(self, area: str) -> List[Dict[str, Any]]:
        self.metrics["web_searches"] += 1
        results = self.web_access.search_scientific(area)
        latest = self.web_access.get_latest_research(area)

        self.logger.info(f"🌐 Интернет-исследование: {area} — {len(results)} источников, {len(latest)} статей")
        return results

    # ================================================================
    #  ТЕОРИИ И ВЫЧИСЛЕНИЯ
    # ================================================================

    def _build_theory(self, area: str) -> AkvaTheory:
        templates = THEORY_TEMPLATES.get(area, THEORY_TEMPLATES["mathematics"])
        name, category, base_value = random.choice(templates)
        scientific_value = min(1.0, base_value + random.uniform(-0.1, 0.1))

        theory = AkvaTheory(
            name=f"{name} (цикл {self.cycle_count})",
            category=category,
            scientific_value=round(scientific_value, 2),
            description=f"Теория в области {area}, построена на {self.cycle_count}-м цикле",
            created_at=datetime.now().isoformat(),
        )

        self.theories.append(theory)
        self.metrics["theories_built"] += 1

        xp = XP_TABLE["build_theory"]
        kl = self.knowledge_levels.get(area)
        if kl:
            kl.add_xp(xp)
            kl.theories_built.append(theory.name)

        self.personality.apply_change({"creativity": 0.01, "confidence": 0.005})
        self.logger.info(f"🔬 Теория: {theory.name} | ценность: {scientific_value:.2f}")
        return theory

    def _perform_calculation(self, area: str) -> AkvaCalculation:
        templates = CALC_TEMPLATES.get(area, CALC_TEMPLATES["mathematics"])
        name, calc_func, formula, units = random.choice(templates)
        result = calc_func()

        calc = AkvaCalculation(
            name=f"{name} (цикл {self.cycle_count})",
            result=result,
            formula=formula,
            units=units,
            verified=random.random() < 0.7,
        )

        self.calculations.append(calc)
        self.metrics["calculations_run"] += 1

        xp = XP_TABLE["run_calculation"]
        kl = self.knowledge_levels.get(area)
        if kl:
            kl.add_xp(xp)
            kl.calculations_done += 1

        self.personality.apply_change({"precision": 0.005, "confidence": 0.005})
        self.logger.info(f"🧮 Расчёт: {name} = {result} {units} | {formula}")
        return calc

    # ================================================================
    #  ОБЩЕНИЕ
    # ================================================================

    def _communicate(self):
        if not self.config.communication_enabled:
            return

        recipient = random.choice(self.config.other_girls)
        roll = random.random()

        if roll < 0.2:
            content = self.communicator.generate_greeting(recipient)
            msg_type = "greeting"
        elif roll < 0.5:
            area = self._select_research_area()
            topic, _ = self._select_topic(area)
            content = self.communicator.generate_knowledge_share(area, topic)
            msg_type = "knowledge_share"
        elif roll < 0.75:
            area = self._select_research_area()
            content = self.communicator.generate_question(recipient, area)
            msg_type = "question"
        else:
            content = self.reporter.generate_summary(
                type('R', (), {'cycle_number': self.cycle_count, 'theories_built': [],
                              'calculations_done': [], 'studied_topics': ['текущий цикл'],
                              'level_changes': [], 'xp_gained': 0})()
            )
            msg_type = "report"

        self.communicator.send_message("akva", recipient, content, msg_type)
        self.metrics["messages_sent"] += 1

        self.personality.apply_change({
            "friendliness": 0.01, "empathy": 0.01, "confidence": 0.005,
        })
        self.logger.info(f"💬 Общение с {recipient}: [{msg_type}]")

    # ================================================================
    #  ЦИКЛ
    # ================================================================

    def _cycle(self):
        self.cycle_count += 1

        # 1. Выбор направления
        area = self._select_research_area()
        topic, is_complex = self._select_topic(area)

        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"🔬 ЦИКЛ ИССЛЕДОВАНИЙ #{self.cycle_count}")
        self.logger.info(f"📚 Направление: {area}")
        self.logger.info(f"📖 Тема: {topic} ({'сложно' if is_complex else 'базово'})")

        # 2. Изучение
        study_xp = self._study_topic(area, topic, is_complex)

        # 3. Интернет-исследование
        if self.config.web_search_enabled and self.cycle_count % self.config.web_search_interval == 0:
            self._web_research(area)
            study_xp += XP_TABLE["web_research"]

        # 4. Построение теории
        theory = self._build_theory(area)
        study_xp += XP_TABLE["build_theory"]

        # 5. Расчёт
        calc = self._perform_calculation(area)
        study_xp += XP_TABLE["run_calculation"]

        # 6. Общение
        if self.config.communication_enabled and self.cycle_count % self.config.communication_interval == 0:
            self._communicate()
            study_xp += XP_TABLE["communicate"]

        # 7. Отчёт
        if self.config.reporting_enabled:
            level_changes = []
            for area_name, kl in self.knowledge_levels.items():
                was_level = kl.level
                kl.add_xp(0)
                if kl.level > was_level:
                    level_changes.append(f"{area_name}: {was_level} → {kl.level}")

            report = self.reporter.generate_cycle_report(
                cycle_number=self.cycle_count,
                personality=self.personality,
                knowledge_levels=self.knowledge_levels,
                studied_topics=[topic],
                theories=[theory.to_dict()],
                calculations=[calc.to_dict()],
                communication=[],
                personality_changes={},
                xp_gained=study_xp,
                level_changes=level_changes,
            )

            if self.config.report_every_cycle:
                self.reporter.save_report(report)
                self.metrics["reports_written"] += 1

            if self.config.summary_to_others:
                summary = self.reporter.generate_summary(report)
                self.communicator.send_to_all(summary, "report")

        # 8. Самоанализ
        if self.config.self_development_enabled and self.cycle_count % self.config.self_assessment_interval == 0:
            self._self_assessment()

        # Итого
        self.metrics["total_xp"] += study_xp
        self.metrics["cycles_completed"] += 1

        if self.cycle_count % self.config.save_state_every_n_cycles == 0:
            self._save_state()
        
        # ================================================================
        #  HUMANITY CYCLE — Настроение, душа, спонтанность
        # ================================================================
        self.humanity.current_cycle = self.cycle_count
        
        event_type = "routine"
        if self.metrics.get("theories_built", 0) > 0 and self.cycle_count % 3 == 0:
            event_type = "success"
        elif random.random() < 0.1:
            event_type = "failure"
        
        humanity_result = self.humanity.cycle_step(event_type=event_type, context="math_research")
        
        if humanity_result.get("thought"):
            self.logger.info(f"💭 Аква думает: {humanity_result['thought']}")
        
        initiative = humanity_result.get("initiative")
        if initiative:
            self._send_spontaneous_message(initiative)
        
        # ================================================================
        #  6 МОДУЛЕЙ ДУШИ — Сознание, Сердце, Амбиции, Воля, Разум
        # ================================================================
        self._soul_cycle()
        
        # ================================================================
        #  EMOTIONAL ENGINE CYCLE — Desire + Belief = Emotion!
        # ================================================================
        self._emotional_cycle()

# Укрепление характера (периодически)
        if self.cycle_count % 5 == 0:
            strengthened = self.character.strengthen_strengths()
            if strengthened > 0:
                self.logger.info(f"Character strengthened: {strengthened} traits")

        # Эволюция характера (периодически)
        if self.cycle_count % 10 == 0:
            evolved = self.character.evolve_traits()
            if evolved:
                self.logger.info("Character evolved")

        self._save_state()

        self.logger.info(f"✅ Цикл #{self.cycle_count} завершён | +{study_xp} XP | Всего: {self.metrics['total_xp']}")
        self.logger.info(f"📊 Характер: {self.personality.dominant_trait()} | Уровень: {self.personality.level_description()}")

    def _self_assessment(self):
        self.logger.info(f"\n🧠 САМОАНАЛИЗ (цикл #{self.cycle_count})")
        for area, kl in self.knowledge_levels.items():
            self.logger.info(f"   {area}: уровень {kl.level}/100, XP: {kl.xp}")
        self.logger.info(f"   Характер: {self.personality.dominant_trait()}")
        self.logger.info(f"   Всего теорий: {len(self.theories)}")
        self.logger.info(f"   Всего вычислений: {len(self.calculations)}")
        weakest = min(self.knowledge_levels.items(), key=lambda x: x[1].level)
        self.logger.info(f"   💡 Рекомендация: углубить {weakest[0]} (уровень {weakest[1].level})")

    # ================================================================
    #  ЗАПУСК
    # ================================================================

    def _should_stop(self) -> bool:
        if self._shutdown_requested:
            return True
        if self.config.max_cycles is not None:
            if self.cycle_count >= self.config.max_cycles:
                return True
        return False

    def run(self):
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info(f"🚀 ЗАПУСК АВТОНОМНОГО ЯДРА АКВА")
        self.logger.info(f"{'=' * 60}")
        self.logger.info(f"Версия: {self.current_version}")
        self.logger.info(f"Фокус: {', '.join(self.config.research_areas)}")
        self.logger.info(f"Характер: {self.personality.level_description()}")
        self.logger.info(f"Интернет: {'✅' if self.config.web_search_enabled else '❌'}")
        self.logger.info(f"Общение: {'✅' if self.config.communication_enabled else '❌'}")
        self.logger.info(f"Отчёты: {'✅' if self.config.reporting_enabled else '❌'}")
        self.logger.info(f"{'=' * 60}\n")

        while not self._should_stop():
            try:
                self._cycle()
                if self.config.cycle_interval > 0:
                    time.sleep(self.config.cycle_interval)
            except KeyboardInterrupt:
                self.logger.info("⚠️ Прервано пользователем")
                break
            except Exception as e:
                self.logger.error(f"❌ Ошибка в цикле: {e}", exc_info=True)
                time.sleep(1)

        self._final_report()
        
        # Укрепление характера (периодически)
        if self.cycle_count % 5 == 0:
            strengthened = self.character.strengthen_strengths()
            if strengthened > 0:
                self.logger.info(f"Character strengthened: {strengthened} traits")

        # Эволюция характера (периодически)
        if self.cycle_count % 10 == 0:
            evolved = self.character.evolve_traits()
            if evolved:
                self.logger.info("Character evolved")

        self._save_state()

    def _final_report(self):
        report = self.reporter.generate_final_report(
            personality=self.personality,
            knowledge_levels=self.knowledge_levels,
            total_cycles=self.cycle_count,
        )
        self.logger.info(f"\n{report}")

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.config.name,
            "version": self.current_version,
            "is_running": not self._should_stop(),
            "cycle_count": self.cycle_count,
            "total_xp": self.metrics["total_xp"],
            "personality": self.personality.to_dict(),
            "personality_level": self.personality.level_description(),
            "knowledge_levels": {
                area: {"level": kl.level, "xp": kl.xp}
                for area, kl in self.knowledge_levels.items()
            },
            "metrics": self.metrics,
            "theories_count": len(self.theories),
            "calculations_count": len(self.calculations),
        }

    def stop(self):
        self._shutdown_requested = True
        self.logger.info("🛑 Аква остановлена")

    # ================================================================
    #  HUMANITY INTEGRATION — Спонтанные сообщения
    # ================================================================

    def _send_spontaneous_message(self, initiative):
        """Отправить спонтанное сообщение сестре на основе инициативы humanity layer."""
        target = initiative["target"]
        topic = initiative["topic"]
        msg_type = initiative["type"]
        
        raw_msg = f"📐 [{msg_type}] {topic}"
        human_msg = self.humanity.humanize_response(raw_msg, event_type="chat")
        
        self.logger.info(f"💬 Аква пишет {target}: {human_msg[:100]}...")
        
        if self.config.communication_enabled:
            try:
                self.communicator.send_message("akva", target, human_msg, msg_type)
                self.metrics["messages_sent"] += 1
                self.logger.info(f"   ✅ Сообщение отправлено {target}")
                
                self.humanity.memory.record_sister_chat(
                    target, topic,
                    self.humanity.mood.current_mood,
                    self.humanity.mood.current_mood
                )
            except Exception as e:
                self.logger.warning(f"Не удалось отправить сообщение: {e}")
