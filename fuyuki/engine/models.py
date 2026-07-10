"""
Модели данных Фуюки.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ElectricityTheoryCategory(Enum):
    """Категории теорий атмосферного электричества."""
    CLASSICAL = "classical"  # Классическая электродинамика
    ATMOSPHERIC = "atmospheric"  # Физика атмосферы
    LIGHTNING = "lightning"  # Физика молний
    BALL_LIGHTNING = "ball_lightning"  # Шаровая молния
    SPRITES = "sprites"  # Спрайты и джеты
    HARVESTING = "harvesting"  # Сбор энергии
    CONTROL = "control"  # Управление разрядами


class CalculationType(Enum):
    """Типы вычислений."""
    ELECTRIC_FIELD = "electric_field"
    LIGHTNING_ENERGY = "lightning_energy"
    CHARGE_SEPARATION = "charge_separation"
    BREAKDOWN_VOLTAGE = "breakdown_voltage"
    BALL_LIGHTNING = "ball_lightning"
    ENERGY_HARVESTING = "energy_harvesting"
    LIGHTNING_PATH = "lightning_path"


@dataclass
class ResearchPaper:
    """Научная статья об атмосферном электричестве."""
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
class ElectricityTheory:
    """Теория атмосферного электричества."""
    id: str
    name: str
    description: str
    category: ElectricityTheoryCategory
    timestamp: str
    equations: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)
    experimental_evidence: List[str] = field(default_factory=list)
    compatibility_score: float = 0.0
    scientific_value: float = 0.0
    validated: bool = False
    source: str = "original"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value if isinstance(self.category, ElectricityTheoryCategory) else self.category,
            "timestamp": self.timestamp,
            "equations": self.equations,
            "predictions": self.predictions,
            "experimental_evidence": self.experimental_evidence,
            "compatibility_score": self.compatibility_score,
            "scientific_value": self.scientific_value,
            "validated": self.validated,
            "source": self.source,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ElectricityTheory":
        """Создать теорию из словаря."""
        category = data.get("category")
        if isinstance(category, str):
            try:
                category = ElectricityTheoryCategory(category)
            except ValueError:
                category = ElectricityTheoryCategory.CLASSICAL
        
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=category,
            timestamp=data["timestamp"],
            equations=data.get("equations", []),
            predictions=data.get("predictions", []),
            experimental_evidence=data.get("experimental_evidence", []),
            compatibility_score=data.get("compatibility_score", 0.0),
            scientific_value=data.get("scientific_value", 0.0),
            validated=data.get("validated", False),
            source=data.get("source", "original"),
        )


@dataclass
class Calculation:
    """Результат вычисления."""
    id: str
    calculation_type: CalculationType
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
            "calculation_type": self.calculation_type.value if isinstance(self.calculation_type, CalculationType) else self.calculation_type,
            "timestamp": self.timestamp,
            "input_params": self.input_params,
            "result": self.result,
            "units": self.units,
            "precision": self.precision,
            "confidence": self.confidence,
            "notes": self.notes,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Calculation":
        """Создать вычисление из словаря."""
        calc_type = data.get("calculation_type")
        if isinstance(calc_type, str):
            try:
                calc_type = CalculationType(calc_type)
            except ValueError:
                calc_type = CalculationType.LIGHTNING_ENERGY
        
        return cls(
            id=data["id"],
            calculation_type=calc_type,
            timestamp=data["timestamp"],
            input_params=data.get("input_params", {}),
            result=data.get("result"),
            units=data.get("units", ""),
            precision=data.get("precision", 6),
            confidence=data.get("confidence", 0.0),
            notes=data.get("notes", ""),
        )


@dataclass
class LightningStrike:
    """Данные о разряде молнии."""
    id: str
    timestamp: str
    current: float  # Амперы
    voltage: float  # Вольты
    duration: float  # секунды
    energy: float  # Джоули
    temperature: float  # Кельвины
    channel_length: float  # метры
    location: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "current": self.current,
            "voltage": self.voltage,
            "duration": self.duration,
            "energy": self.energy,
            "temperature": self.temperature,
            "channel_length": self.channel_length,
            "location": self.location,
        }


@dataclass
class ElectricityConstants:
    """Физические константы."""
    epsilon_0: float = 8.854187817e-12  # Электрическая постоянная, Ф/м
    e: float = 1.602176634e-19  # Элементарный заряд, Кл
    m_e: float = 9.10938356e-31  # Масса электрона, кг
    E_breakdown_air: float = 3e6  # Пробивное напряжение воздуха, В/м
    typical_lightning_current: float = 30000  # Типичный ток молнии, А
    typical_lightning_voltage: float = 1e8  # Типичное напряжение молнии, В
    typical_lightning_duration: float = 0.0003  # Длительность молнии, с
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "epsilon_0": self.epsilon_0,
            "e": self.e,
            "m_e": self.m_e,
            "E_breakdown_air": self.E_breakdown_air,
            "typical_lightning_current": self.typical_lightning_current,
            "typical_lightning_voltage": self.typical_lightning_voltage,
            "typical_lightning_duration": self.typical_lightning_duration,
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
