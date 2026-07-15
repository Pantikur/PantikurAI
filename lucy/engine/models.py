"""
Модели данных системы Люси — инженера двигателей.

Содержит:
  - EngineType, PropulsionPrinciple — типы двигателей
  - EngineDesign, Calculation — проектирование и расчёты
  - ResearchPaper, Theory — исследования и теории
  - KnowledgeLevel, KnowledgeDomain — уровни знаний
  - LightningStrike — данные об атмосферном электричестве
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class EngineType(Enum):
    """Тип двигателя."""
    PISTON = "piston"              # Поршневой
    TURBINE = "turbine"            # Турбинный
    ROCKET = "rocket"              # Ракетный
    ION = "ion"                    # Ионный
    PLASMA = "plasma"              # Плазменный
    MHD = "mhd"                    # Магнитогидродинамический
    PHOTON = "photon"              # Фотонный
    ANNIHILATION = "annihilation"  # Аннигиляционный
    GRAVITATIONAL = "gravitational"  # Гравитационный
    HYBRID = "hybrid"              # Гибридный


class PropulsionPrinciple(Enum):
    """Принцип тяги."""
    CHEMICAL = "chemical"          # Химический
    ELECTRIC = "electric"          # Электрический
    ELECTROMAGNETIC = "electromagnetic"  # Электромагнитный
    THERMAL = "thermal"            # Тепловой
    NUCLEAR = "nuclear"            # Ядерный
    GRAVITATIONAL = "gravitational"  # Гравитационный
    ANTI_GRAVITY = "anti_gravity"  # Антигравитация


class KnowledgeDomain(Enum):
    """Область знаний."""
    ENGINE_DESIGN = "engine_design"
    PROPULSION = "propulsion"
    GRAVITY = "gravity"
    ATMOSPHERIC_ELECTRICITY = "atmospheric_electricity"
    ENERGY = "energy"
    MATERIALS = "materials"
    CONTROL = "control"


# =====================================================================
#  ДАННЫЕ ДВИГАТЕЛЕЙ
# =====================================================================

@dataclass
class EngineDesign:
    """Проект двигателя."""
    name: str
    engine_type: EngineType
    propulsion_principle: PropulsionPrinciple
    thrust: float = 0.0             # Ньютон
    specific_impulse: float = 0.0   # секунда
    efficiency: float = 0.0         # 0-1
    mass: float = 0.0               # кг
    power_consumption: float = 0.0  # Вт
    feasibility_score: float = 0.0  # 0-1
    gravity_theory_used: Optional[str] = None
    electricity_theory_used: Optional[str] = None
    description: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "engine_type": self.engine_type.value,
            "propulsion_principle": self.propulsion_principle.value,
            "thrust": self.thrust,
            "specific_impulse": self.specific_impulse,
            "efficiency": self.efficiency,
            "mass": self.mass,
            "power_consumption": self.power_consumption,
            "feasibility_score": self.feasibility_score,
            "gravity_theory_used": self.gravity_theory_used,
            "electricity_theory_used": self.electricity_theory_used,
            "description": self.description,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EngineDesign":
        data["engine_type"] = EngineType(data["engine_type"])
        data["propulsion_principle"] = PropulsionPrinciple(data["propulsion_principle"])
        return cls(**data)


@dataclass
class Calculation:
    """Расчёт параметров двигателя."""
    calc_type: str                  # thrust, specific_impulse, efficiency, power
    input_params: dict[str, float]  # входные параметры
    result: float                   # результат
    units: str                      # единицы измерения
    description: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "calc_type": self.calc_type,
            "input_params": self.input_params,
            "result": self.result,
            "units": self.units,
            "description": self.description,
            "timestamp": self.timestamp,
        }


# =====================================================================
#  ИССЛЕДОВАНИЯ И ТЕОРИИ
# =====================================================================

@dataclass
class ResearchPaper:
    """Научная статья."""
    title: str
    authors: list[str]
    year: int
    source: str
    url: Optional[str] = None
    abstract: str = ""
    keywords: list[str] = field(default_factory=list)
    xp_reward: int = 50

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "source": self.source,
            "url": self.url,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "xp_reward": self.xp_reward,
        }


@dataclass
class ElectricityTheory:
    """Теория атмосферного электричества."""
    name: str
    category: str                   # lightning, ball_lightning, sprites, harvesting, control
    description: str
    scientific_value: float = 0.0   # 0-1
    related_papers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "scientific_value": self.scientific_value,
            "related_papers": self.related_papers,
        }


# =====================================================================
#  ЗНАНИЯ И УРОВНИ
# =====================================================================

@dataclass
class KnowledgeLevel:
    """Уровень знаний."""
    current_level: int = 1
    current_xp: int = 0
    level_name: str = "Механик"

    @property
    def progress_to_next(self) -> float:
        levels = [
            (0, "Механик"), (100, "Техник"), (300, "Инженер"),
            (600, "Мл. инженер"), (1000, "Инженер-проектировщик"),
            (1500, "Ст. инженер"), (2200, "Ведущий инженер"),
            (3000, "Кандидат инженерных наук"), (4000, "Доцент по двигателям"),
            (5500, "Профессор пропульсии"), (7000, "Ведущий исследователь"),
            (9000, "Зав. лабораторией"), (11000, "Доктор инженерных наук"),
            (13500, "Проф. мирового уровня"), (16500, "Легенда двигателестроения"),
            (20000, "Гений пропульсии"), (24000, "Мастер гравитации"),
            (28500, "Повелитель двигателей"), (34000, "Хранитель пропульсии"),
            (40000, "Бог Двигателей"),
        ]
        if self.current_level >= 20:
            return 100.0
        next_xp = levels[self.current_level][0]
        prev_xp = levels[self.current_level - 1][0]
        return (self.current_xp - prev_xp) / (next_xp - prev_xp) * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_level": self.current_level,
            "current_xp": self.current_xp,
            "level_name": self.level_name,
        }


# =====================================================================
#  ХАРАКТЕР
# =====================================================================

@dataclass
class CharacterTraits:
    """Черты характера."""
    temperament: str = "холерик"          # холерик, сангвиник, флегматик, меланхолик
    sociality: str = "выборочная"          # интроверт, экстраверт, амбиверт
    emotionality: str = "интенсивная"      # эмоциональная, рациональная
    worldview: str = "инноватор"           # оптимист, пессимист, реалист
    dominance: str = "амбициозная"         # доминантная, сабмиссивная
    change_attitude: str = "энергичная"    # консерватор, прогрессивный
    complexity: str = "динамичная"         # простая, сложная

    # Интенсивность черт (0-1)
    specialty_passion: float = 0.95
    curiosity: float = 0.95
    courage: float = 0.85
    patience: float = 0.75
    creativity: float = 0.90
    collaboration: float = 0.80

    def to_dict(self) -> dict[str, Any]:
        return {
            "temperament": self.temperament,
            "sociality": self.sociality,
            "emotionality": self.emotionality,
            "worldview": self.worldview,
            "dominance": self.dominance,
            "change_attitude": self.change_attitude,
            "complexity": self.complexity,
            "specialty_passion": self.specialty_passion,
            "curiosity": self.curiosity,
            "courage": self.courage,
            "patience": self.patience,
            "creativity": self.creativity,
            "collaboration": self.collaboration,
        }
