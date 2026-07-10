"""
Модели данных Люси.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class EngineType(Enum):
    """Типы двигателей."""
    CHEMICAL = "chemical"  # Химический
    ION = "ion"  # Ионный
    PLASMA = "plasma"  # Плазменный
    PHOTON = "photon"  # Фотонный
    GRAVITY = "gravity"  # Гравитационный
    ELECTRIC = "electric"  # Электрический
    HYBRID = "hybrid"  # Гибридный (гравитация + электричество)
    ANTI_GRAVITY = "anti_gravity"  # Антигравитационный
    LIGHTNING = "lightning"  # Молниевый


class PropulsionPrinciple(Enum):
    """Принципы движения."""
    REACTION = "reaction"  # Реактивная тяга
    ELECTROMAGNETIC = "electromagnetic"  # Электромагнитный
    GRAVITATIONAL = "gravitational"  # Гравитационный
    LIGHT_PRESSURE = "light_pressure"  # Световое давление
    SPACE_TIME = "space_time"  # Искривление пространства-времени


@dataclass
class ResearchPaper:
    """Научная статья о двигателях."""
    title: str
    authors: List[str]
    year: int
    journal: str
    abstract: str
    url: Optional[str] = None
    citations: int = 0
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "journal": self.journal,
            "abstract": self.abstract,
            "url": self.url,
            "citations": self.citations,
            "relevance_score": self.relevance_score,
        }


@dataclass
class EngineDesign:
    """Проект двигателя."""
    id: str
    name: str
    description: str
    engine_type: EngineType
    principle: PropulsionPrinciple
    timestamp: str
    thrust: float  # Ньютоны
    specific_impulse: float  # секунды
    power_requirement: float  # Ватты
    mass: float  # кг
    efficiency: float  # 0-1
    feasibility_score: float  # 0-1
    gravity_theory_used: Optional[str] = None
    electricity_theory_used: Optional[str] = None
    equations: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    validated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "engine_type": self.engine_type.value if isinstance(self.engine_type, EngineType) else self.engine_type,
            "principle": self.principle.value if isinstance(self.principle, PropulsionPrinciple) else self.principle,
            "timestamp": self.timestamp,
            "thrust": self.thrust,
            "specific_impulse": self.specific_impulse,
            "power_requirement": self.power_requirement,
            "mass": self.mass,
            "efficiency": self.efficiency,
            "feasibility_score": self.feasibility_score,
            "gravity_theory_used": self.gravity_theory_used,
            "electricity_theory_used": self.electricity_theory_used,
            "equations": self.equations,
            "components": self.components,
            "risks": self.risks,
            "validated": self.validated,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EngineDesign":
        """Создать проект из словаря."""
        # Безопасное преобразование строк в Enum
        engine_type = data.get("engine_type", EngineType.CHEMICAL)
        if isinstance(engine_type, str):
            try:
                engine_type = EngineType(engine_type)
            except ValueError:
                engine_type = EngineType.CHEMICAL
        
        principle = data.get("principle", PropulsionPrinciple.REACTION)
        if isinstance(principle, str):
            try:
                principle = PropulsionPrinciple(principle)
            except ValueError:
                principle = PropulsionPrinciple.REACTION
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            engine_type=engine_type,
            principle=principle,
            timestamp=data["timestamp"],
            thrust=data["thrust"],
            specific_impulse=data["specific_impulse"],
            power_requirement=data["power_requirement"],
            mass=data["mass"],
            efficiency=data["efficiency"],
            feasibility_score=data["feasibility_score"],
            gravity_theory_used=data.get("gravity_theory_used"),
            electricity_theory_used=data.get("electricity_theory_used"),
            equations=data.get("equations", []),
            components=data.get("components", []),
            risks=data.get("risks", []),
            validated=data.get("validated", False),
        )


@dataclass
class Calculation:
    """Результат расчёта."""
    id: str
    calculation_type: str
    timestamp: str
    input_params: Dict[str, Any]
    result: Any
    units: str
    precision: int
    confidence: float
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "calculation_type": self.calculation_type,
            "timestamp": self.timestamp,
            "input_params": self.input_params,
            "result": self.result,
            "units": self.units,
            "precision": self.precision,
            "confidence": self.confidence,
            "notes": self.notes,
        }


@dataclass
class EngineConstants:
    """Инженерные константы."""
    g_earth: float = 9.80665  # м/с²
    c: float = 299792458.0  # м/с
    standard_gravity: float = 9.80665  # м/с²
    sea_level_pressure: float = 101325.0  # Па
    air_density: float = 1.225  # кг/м³
    
    # Типичные параметры двигателей
    chemical_isp: float = 450.0  # с (макс для химических)
    ion_isp: float = 5000.0  # с
    plasma_isp: float = 10000.0  # с
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "g_earth": self.g_earth,
            "c": self.c,
            "standard_gravity": self.standard_gravity,
            "sea_level_pressure": self.sea_level_pressure,
            "air_density": self.air_density,
            "chemical_isp": self.chemical_isp,
            "ion_isp": self.ion_isp,
            "plasma_isp": self.plasma_isp,
        }


@dataclass
class ResearchRecord:
    """Запись исследования."""
    timestamp: str
    research_type: str
    description: str
    outcome: str
    data: Dict[str, Any] = field(default_factory=dict)
    validated: bool = False
    published: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "research_type": self.research_type,
            "description": self.description,
            "outcome": self.outcome,
            "data": self.data,
            "validated": self.validated,
            "published": self.published,
        }
