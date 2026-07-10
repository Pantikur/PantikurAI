"""
Модели данных Ханако.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class TheoryCategory(Enum):
    """Категории гравитационных теорий."""
    CLASSICAL = "classical"  # Классическая механика
    RELATIVITY = "relativity"  # Общая теория относительности
    QUANTUM = "quantum"  # Квантовая гравитация
    MODIFIED = "modified"  # Модифицированная гравитация
    UNIFIED = "unified"  # Единая теория
    SPECULATIVE = "speculative"  # Спекулятивные теории


class CalculationType(Enum):
    """Типы вычислений."""
    GRAVITATIONAL_FORCE = "gravitational_force"
    ESCAPE_VELOCITY = "escape_velocity"
    ORBITAL_PERIOD = "orbital_period"
    TIME_DILATION = "time_dilation"
    BLACK_HOLE = "black_hole"
    GRAVITATIONAL_WAVES = "gravitational_waves"
    ANTI_GRAVITY = "anti_gravity"


@dataclass
class ResearchPaper:
    """Научная статья о гравитации."""
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
class GravityTheory:
    """Гравитационная теория."""
    id: str
    name: str
    description: str
    category: TheoryCategory
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
            "category": self.category.value if isinstance(self.category, TheoryCategory) else self.category,
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
    def from_dict(cls, data: Dict[str, Any]) -> "GravityTheory":
        """Создать теорию из словаря."""
        category = data.get("category", TheoryCategory.SPECULATIVE)
        if isinstance(category, str):
            try:
                category = TheoryCategory(category)
            except ValueError:
                category = TheoryCategory.SPECULATIVE
        
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
        calc_type = data.get("calculation_type", CalculationType.GRAVITATIONAL_FORCE)
        if isinstance(calc_type, str):
            try:
                calc_type = CalculationType(calc_type)
            except ValueError:
                calc_type = CalculationType.GRAVITATIONAL_FORCE
        
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
class Experiment:
    """Гравитационный эксперимент."""
    id: str
    name: str
    description: str
    timestamp: str
    setup: str
    procedure: List[str]
    results: Dict[str, Any]
    success: bool
    safety_verified: bool = True
    risks: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "timestamp": self.timestamp,
            "setup": self.setup,
            "procedure": self.procedure,
            "results": self.results,
            "success": self.success,
            "safety_verified": self.safety_verified,
            "risks": self.risks,
        }


@dataclass
class ResearchRecord:
    """Запись исследования."""
    timestamp: str
    research_type: str  # "theory", "calculation", "experiment", "web_search"
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


@dataclass
class GravityConstants:
    """Гравитационные константы."""
    G: float = 6.67430e-11  # Гравитационная постоянная, м³/(кг·с²)
    c: float = 299792458.0  # Скорость света, м/с
    h: float = 6.62607015e-34  # Постоянная Планка, Дж·с
    g_earth: float = 9.80665  # Ускорение свободного падения на Земле, м/с²
    M_earth: float = 5.972e24  # Масса Земли, кг
    R_earth: float = 6.371e6  # Радиус Земли, м
    M_sun: float = 1.989e30  # Масса Солнца, кг
    R_sun: float = 6.9634e8  # Радиус Солнца, м
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "G": self.G,
            "c": self.c,
            "h": self.h,
            "g_earth": self.g_earth,
            "M_earth": self.M_earth,
            "R_earth": self.R_earth,
            "M_sun": self.M_sun,
            "R_sun": self.R_sun,
        }
