"""
Celesta — Модули интимных знаний.

Описывает:
- Этапы интимной жизни (от прикосновений до последствий)
- Категории знаний
- Модули изучения
"""

import json
import time
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


class IntimacyStage(Enum):
    """
    Этапы интимной жизни.
    
    Система изучает каждый этап последовательно:
    1. Прикосновения → 2. Возбуждение → 3. Интим → 4. Последствия
    """
    TOUCH = "touch"                           # Этап 1: Прикосновения
    AROUSAL = "arousal"                       # Этап 2: Возбуждение
    INTIMACY = "intimacy"                     # Этап 3: Интимный процесс
    POST_INTIMACY = "post_intimacy"           # Этап 4: После интима
    EXCESSIVE = "excessive"                   # Этап 5: Избыточный интим
    INTERRUPTED = "interrupted"               # Этап 6: Прерванный процесс
    CONSEQUENCES = "consequences"             # Этап 7: Последствия
    RECOVERY = "recovery"                     # Этап 8: Восстановление
    FULL_UNDERSTANDING = "full_understanding" # Этап 9: Полное понимание


class IntimacyCategory(Enum):
    """Категории интимных знаний."""
    PHYSIOLOGICAL = "physiological"           # Физиология
    PSYCHOLOGICAL = "psychological"           # Психология
    HORMONAL = "hormonal"                     # Гормональные эффекты
    REPRODUCTIVE = "reproductive"             # Репродуктивная система
    PATHOLOGICAL = "pathological"             # Патологии и последствия
    RECOVERY = "recovery"                     # Восстановление
    RACE_SPECIFIC = "race_specific"           # Особенности по расам


class IntimacyModule:
    """
    Модуль интимных знаний.
    
    Примеры:
    - TouchModule — изучение прикосновений
    - HormonalModule — гормональные эффекты
    - ConsequencesModule — последствия
    """
    
    def __init__(self, name: str, category: IntimacyCategory, description: str = ""):
        self.name = name
        self.category = category
        self.description = description
        self.knowledge_points: List[Dict[str, Any]] = []
        self.research_progress = 0.0
        self.stages_covered: List[IntimacyStage] = []
        self.race_variants: Dict[str, List[Dict[str, Any]]] = {}
        self.created_at = time.time()
        self.updated_at = time.time()
    
    def add_knowledge(self, point: str, details: Optional[Dict[str, Any]] = None, stage: Optional[IntimacyStage] = None):
        """Добавить точку знания."""
        kp = {
            "point": point,
            "details": details or {},
            "stage": stage.value if stage else None,
            "timestamp": time.time()
        }
        self.knowledge_points.append(kp)
        self.updated_at = time.time()
        self.research_progress = min(1.0, self.research_progress + 0.05)
        
        if stage and stage not in self.stages_covered:
            self.stages_covered.append(stage)
    
    def add_race_variant(self, race: str, variant: Dict[str, Any]):
        """Добавить вариант для расы."""
        if race not in self.race_variants:
            self.race_variants[race] = []
        self.race_variants[race].append({
            **variant,
            "added_at": time.time()
        })
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "knowledge_count": len(self.knowledge_points),
            "research_progress": self.research_progress,
            "stages_covered": [s.value for s in self.stages_covered],
            "race_variants_count": sum(len(v) for v in self.race_variants.values()),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


def create_default_modules() -> Dict[str, IntimacyModule]:
    """
    Создать стандартный набор модулей интимных знаний.
    
    Каждый модуль описывает область, которую нужно изучить.
    """
    modules = {}
    
    # === МОДУЛЬ ПРИКОСНОВЕНИЙ ===
    touch = IntimacyModule(
        name="touch_system",
        category=IntimacyCategory.PHYSIOLOGICAL,
        description="Изучение прикосновений: виды, эффекты, физиология"
    )
    touch.add_knowledge(
        "Кожа содержит ~5 миллионов рецепторов",
        {"receptors": ["meissner", "pacinian", "merkel", "ruffini"], "density": "high"},
        IntimacyStage.TOUCH
    )
    touch.add_knowledge(
        "Лёгкие прикосновения активируют C-волокна",
        {"fiber_type": "C-tactile", "response": "pleasure", "speed_ms": 1},
        IntimacyStage.TOUCH
    )
    touch.add_knowledge(
        "Интенсивные прикосновения активируют A-дельта волокна",
        {"fiber_type": "A-delta", "response": "pressure", "speed_ms": 20},
        IntimacyStage.TOUCH
    )
    touch.add_knowledge(
        "Оральной сенсорикой управляют 2/3 коры мозга",
        {"cortex_ratio": 0.33, "sensitivity": "very_high"},
        IntimacyStage.TOUCH
    )
    touch.add_knowledge(
        "Тактильная депривация вызывает стресс",
        {"effects": ["cortisol_up", "anxiety", "immune_down"], "threshold_days": 3},
        IntimacyStage.TOUCH
    )
    modules["touch_system"] = touch
    
    # === МОДУЛЬ ВОЗБУЖДЕНИЯ ===
    arousal = IntimacyModule(
        name="arousal_system",
        category=IntimacyCategory.PHYSIOLOGICAL,
        description="Физиология и психология возбуждения"
    )
    arousal.add_knowledge(
        "Возбуждение начинается с мозговых центров",
        {"centers": ["hypothalamus", "amygdala", "prefrontal"], "trigger": "sensory"},
        IntimacyStage.AROUSAL
    )
    arousal.add_knowledge(
        "Парасимпатическая система отвечает за эрекцию/лубрикацию",
        {"system": "parasympathetic", "neurotransmitter": "NO", "response_time_s": 30},
        IntimacyStage.AROUSAL
    )
    arousal.add_knowledge(
        "Симпатическая система отвечает за оргазм",
        {"system": "sympathetic", "response": "emission", "duration_s": 10},
        IntimacyStage.AROUSAL
    )
    arousal.add_knowledge(
        "Фазы возбуждения: желание → возбуждение → плато",
        {"phases": 4, "total_duration_min": "15-45", "hormones": ["dopamine", "norepinephrine"]},
        IntimacyStage.AROUSAL
    )
    arousal.add_knowledge(
        "Психологические факторы влияют на 70% возбуждения",
        {"factors": ["emotion", "trust", "stress", "environment"], "impact_percent": 70},
        IntimacyStage.AROUSAL
    )
    modules["arousal_system"] = arousal
    
    # === МОДУЛЬ ИНТИМНОГО ПРОЦЕССА ===
    intimacy = IntimacyModule(
        name="intimacy_process",
        category=IntimacyCategory.REPRODUCTIVE,
        description="Физиология интимного процесса"
    )
    intimacy.add_knowledge(
        "Оргазм вызывает выброс окситоцина и пролактина",
        {"hormones": ["oxytocin", "prolactin", "endorphins"], "duration_min": 0.5},
        IntimacyStage.INTIMACY
    )
    intimacy.add_knowledge(
        "Сердцебиение достигает 100-180 уд/мин во время оргазма",
        {"heart_rate_max": 180, "bp_increase_percent": 30, "duration_s": 10},
        IntimacyStage.INTIMACY
    )
    intimacy.add_knowledge(
        "Сперматозоид достигает яйцеклетки за 5-30 минут",
        {"speed_mm_min": 3, "survival_hours": 24, "fertility_window": "5_days"},
        IntimacyStage.INTIMACY
    )
    intimacy.add_knowledge(
        "Женский оргазм может вызывать маточные сокращения",
        {"contraction_frequency": "0.5-1.5_sec", "purpose": "sperm_transport"},
        IntimacyStage.INTIMACY
    )
    modules["intimacy_process"] = intimacy
    
    # === МОДУЛЬ ИЗБЫТОЧНОГО ИНТИМА ===
    excessive = IntimacyModule(
        name="excessive_intimacy",
        category=IntimacyCategory.PATHOLOGICAL,
        description="Последствия избыточного интимного процесса"
    )
    excessive.add_knowledge(
        "Частый интим истощает запасы цинка",
        {"mineral": "zinc", "loss_per_event_mg": 3, "recovery_days": 2},
        IntimacyStage.EXCESSIVE
    )
    excessive.add_knowledge(
        "Избыток пролактина подавляет тестостерон",
        {"hormone": "prolactin", "testosterone_drop_percent": 25, "refractory_period_h": "12-48"},
        IntimacyStage.EXCESSIVE
    )
    excessive.add_knowledge(
        "Хроническая усталость от чрезмерной активности",
        {"symptoms": ["fatigue", "irritability", "libido_down"], "recovery_days": "3-7"},
        IntimacyStage.EXCESSIVE
    )
    excessive.add_knowledge(
        "Раздражение тканей при частом процессе",
        {"tissue_damage": "microabrasions", "healing_hours": "12-24", "infection_risk": "high"},
        IntimacyStage.EXCESSIVE
    )
    excessive.add_knowledge(
        "Психологическая зависимость от дофамина",
        {"neurotransmitter": "dopamine", "tolerance_buildup": "weeks", "withdrawal": "irritability"},
        IntimacyStage.EXCESSIVE
    )
    excessive.add_knowledge(
        "Длительные последствия: гормональный дисбаланс",
        {"effects": ["low_testosterone", "high_prolactin", "cortisol_imbalance"], "recovery_months": "1-3"},
        IntimacyStage.EXCESSIVE
    )
    modules["excessive_intimacy"] = excessive
    
    # === МОДУЛЬ ПРЕРВАННОГО ПРОЦЕССА ===
    interrupted = IntimacyModule(
        name="interrupted_process",
        category=IntimacyCategory.PATHOLOGICAL,
        description="Последствия прерванного интимного процесса"
    )
    interrupted.add_knowledge(
        "Прерванное возбуждение вызывает венозный застой",
        {"condition": "pelvic_congestion", "symptoms": ["aching", "pressure", "swelling"], "duration_h": "6-24"},
        IntimacyStage.INTERRUPTED
    )
    interrupted.add_knowledge(
        "Невысвобожденный семенной материал резорбируется",
        {"process": "phagocytosis", "duration_days": "2-3", "symptoms": ["epididymal_pressure"]},
        IntimacyStage.INTERRUPTED
    )
    interrupted.add_knowledge(
        "Психологический стресс от прерывания",
        {"hormones": ["cortisol_up", "adrenaline_up"], "effects": ["frustration", "anxiety"]},
        IntimacyStage.INTERRUPTED
    )
    interrupted.add_knowledge(
        "Ретроградная эякуляция при насильственном прерывании",
        {"condition": "retrograde", "risk": "bladder_damage", "long_term": "infertility"},
        IntimacyStage.INTERRUPTED
    )
    interrupted.add_knowledge(
        "Хроническое прерывание ведёт к простатиту",
        {"condition": "chronic_prostatitis", "symptoms": ["pain", "dysfunction", "frequency"], "recovery_months": "3-12"},
        IntimacyStage.INTERRUPTED
    )
    interrupted.add_knowledge(
        "Нарушение условных рефлексов",
        {"condition": "conditioned_reflex_disruption", "effects": ["ed_dysfunction", "premature_ejaculation"]},
        IntimacyStage.INTERRUPTED
    )
    modules["interrupted_process"] = interrupted
    
    # === МОДУЛЬ ПОСЛЕДСТВИЙ ===
    consequences = IntimacyModule(
        name="consequences_system",
        category=IntimacyCategory.PATHOLOGICAL,
        description="Общие последствия интимной жизни"
    )
    consequences.add_knowledge(
        "ИМТ и вес влияют на фертильность",
        {"optimal_range": "18.5-24.9", "impact": "sperm_quality_oocyte_quality"},
        IntimacyStage.CONSEQUENCES
    )
    consequences.add_knowledge(
        "Стресс снижает фертильность на 40%",
        {"mechanism": "cortisol_suppresses_gnRH", "reversible": True},
        IntimacyStage.CONSEQUENCES
    )
    consequences.add_knowledge(
        "После интима иммунитет повышается на 30%",
        {"immunoglobulin": "IgA", "increase_percent": 30, "duration_hours": 12},
        IntimacyStage.CONSEQUENCES
    )
    consequences.add_knowledge(
        "Окситоцин снижает тревожность",
        {"hormone": "oxytocin", "effect": "anxiety_down", "bonding": True},
        IntimacyStage.CONSEQUENCES
    )
    modules["consequences_system"] = consequences
    
    # === МОДУЛЬ ВОССТАНОВЛЕНИЯ ===
    recovery = IntimacyModule(
        name="recovery_system",
        category=IntimacyCategory.RECOVERY,
        description="Процессы восстановления после интима"
    )
    recovery.add_knowledge(
        "Рефрактерный период: мужчины 15 мин — 48 часов",
        {"factor": "prolactin_level", "age_dependent": True, "average_h": 1},
        IntimacyStage.RECOVERY
    )
    recovery.add_knowledge(
        "Восстановление цинка: 2-3 дня при нормальном питании",
        {"diet_source": ["oyster", "pumpkin_seed", "beef"], "supplement_mg": 15},
        IntimacyStage.RECOVERY
    )
    recovery.add_knowledge(
        "Сон после интима помогает восстановлению",
        {"hormone": "growth_hormone", "sleep_hours_needed": 7, "recovery_boost_percent": 40},
        IntimacyStage.RECOVERY
    )
    recovery.add_knowledge(
        "Гидратация ускоряет выведение токсинов",
        {"water_liters_per_day": 2, "toxin_clearance_hours": 12},
        IntimacyStage.RECOVERY
    )
    modules["recovery_system"] = recovery
    
    # === МОДУЛЬ РАСОВЫХ ОСОБЕННОСТЕЙ ===
    race_specific = IntimacyModule(
        name="race_specific_intimacy",
        category=IntimacyCategory.RACE_SPECIFIC,
        description="Особенности интимной жизни по расам и типам существ"
    )
    race_specific.add_knowledge(
        "Люди: стандартная физиология, гормональные циклы 24-28 дней",
        {"cycle_days": "24-28", "fertility_window": "5_days", "refractory_h": "1-48"},
        IntimacyStage.FULL_UNDERSTANDING
    )
    race_specific.add_knowledge(
        "Эльфы: замедленный метаболизм, длительные фазы возбуждения",
        {"arousal_duration_multiplier": 2, "hormone_sensitivity": "high", "bonding_strength": "very_strong"},
        IntimacyStage.FULL_UNDERSTANDING
    )
    race_specific.add_knowledge(
        "Демоны: повышенная выносливость, быстрый рефрактерный период",
        {"stamina_multiplier": 3, "refractory_multiplier": 0.3, "hormone_intensity": "extreme"},
        IntimacyStage.FULL_UNDERSTANDING
    )
    race_specific.add_knowledge(
        "Нежить: отсутствие репродуктивной функции, но сохранение сенсорики",
        {"reproductive": False, "sensory_preserved": True, "hormonal": False},
        IntimacyStage.FULL_UNDERSTANDING
    )
    race_specific.add_knowledge(
        "Элементали: энергетическая обменность вместо физической",
        {"mechanism": "energy_exchange", "physical_contact": False, "bonding": "telepathic"},
        IntimacyStage.FULL_UNDERSTANDING
    )
    modules["race_specific_intimacy"] = race_specific
    
    return modules
