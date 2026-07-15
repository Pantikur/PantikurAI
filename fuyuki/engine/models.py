"""
Модели данных Фуюки — исследователя атмосферного электричества.

Содержит:
  - ElectricityTheory — теории атмосферного электричества
  - ResearchPaper — изученные научные статьи
  - Calculation — электрические вычисления
  - ResearchRecord — запись исследования
  - LightningStrike — данные о молниях
  - KnowledgeLevel — уровень знаний и прогресс
  - ElectricityConstants — физические константы
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================


class ElectricityTheoryCategory(Enum):
    """Категории теорий атмосферного электричества."""
    CLASSICAL = "classical"             # Классическая электродинамика
    ATMOSPHERIC = "atmospheric"         # Атмосферное электричество
    LIGHTNING = "lightning"             # Молнии
    BALL_LIGHTNING = "ball_lightning"   # Шаровая молния
    SPRITES = "sprites"                 # Верхнеатмосферные разряды
    HARVESTING = "harvesting"           # Сбор энергии
    CONTROL = "control"                 # Управление молниями


class CalculationType(Enum):
    """Типы электрических вычислений."""
    ELECTRIC_FIELD = "electric_field"       # Электрическое поле
    LIGHTNING_ENERGY = "lightning_energy"   # Энергия молнии
    CHARGE_SEPARATION = "charge_separation" # Разделение зарядов
    BREAKDOWN_VOLTAGE = "breakdown_voltage" # Пробивное напряжение
    BALL_LIGHTNING = "ball_lightning"       # Шаровая молния
    ENERGY_HARVESTING = "energy_harvesting" # Сбор энергии
    LIGHTNING_PATH = "lightning_path"       # Путь молнии


class KnowledgeDomain(Enum):
    """Области знаний Фуюки."""
    ATMOSPHERIC_ELECTRICITY = "atmospheric_electricity"
    LIGHTNING_PHYSICS = "lightning_physics"
    ELECTROMAGNETISM = "electromagnetism"
    PLASMA_PHYSICS = "plasma_physics"
    ENERGY_HARVESTING = "energy_harvesting"
    PROTECTION_SYSTEMS = "protection_systems"
    PROJECT_CODE = "project_code"
    GENERAL_SCIENCE = "general_science"


# =====================================================================
#  ЭЛЕКТРИЧЕСКИЕ КОНСТАНТЫ
# =====================================================================


@dataclass
class ElectricityConstants:
    """Физические константы для вычислений."""
    # Постоянные
    epsilon_0: float = 8.854e-12          # Диэлектрическая проницаемость вакуума (Ф/м)
    mu_0: float = 4 * 3.14159e-7          # Магнитная постоянная (Гн/м)
    c: float = 299792458.0                # Скорость света (м/с)
    e: float = 1.602e-19                  # Элементарный заряд (Кл)
    me: float = 9.109e-31                 # Масса электрона (кг)
    mp: float = 1.673e-27                 # Масса протона (кг)

    # Атмосферные
    E_breakdown_air: float = 3e6          # Поле пробоя воздуха (В/м)
    fair_weather_field: float = 100.0     # Поле ясной погоды (В/м)
    ionosphere_potential: float = 300000.0 # Потенциал ионосферы (В)
    earth_potential: float = 0.0          # Потенциал земли (В)

    # Молнии
    typical_lightning_current: float = 30000.0    # Ток молнии (А)
    typical_lightning_voltage: float = 1e9        # Напряжение молнии (В)
    typical_lightning_duration: float = 0.0002    # Длительность молнии (с)
    typical_lightning_energy: float = 1e9         # Энергия молнии (Дж)
    typical_lightning_charge: float = 15.0        # Заряд молнии (Кл)
    typical_lightning_temperature: float = 30000.0 # Температура канала (К)


# =====================================================================
#  ТЕОРИИ И ИССЛЕДОВАНИЯ
# =====================================================================


@dataclass
class ResearchPaper:
    """Изученная научная статья."""
    title: str
    authors: list[str]
    year: int
    source: str                     # Источник (journal, arxiv, web)
    url: str = ""
    summary: str = ""
    key_findings: list[str] = field(default_factory=list)
    relevance_score: float = 0.0    # Релевантность для Фуюки (0-1)
    studied: bool = False
    studied_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "source": self.source,
            "url": self.url,
            "summary": self.summary,
            "key_findings": self.key_findings,
            "relevance_score": self.relevance_score,
            "studied": self.studied,
            "studied_at": self.studied_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchPaper":
        return cls(
            title=data["title"],
            authors=data.get("authors", []),
            year=data.get("year", 2024),
            source=data.get("source", "web"),
            url=data.get("url", ""),
            summary=data.get("summary", ""),
            key_findings=data.get("key_findings", []),
            relevance_score=data.get("relevance_score", 0.0),
            studied=data.get("studied", False),
            studied_at=data.get("studied_at", ""),
        )


@dataclass
class ElectricityTheory:
    """Теория атмосферного электричества."""
    id: str
    name: str
    description: str
    category: ElectricityTheoryCategory
    timestamp: str
    equations: list[str] = field(default_factory=list)
    predictions: list[str] = field(default_factory=list)
    experimental_evidence: list[str] = field(default_factory=list)
    compatibility_score: float = 0.0
    scientific_value: float = 0.0
    validated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "timestamp": self.timestamp,
            "equations": self.equations,
            "predictions": self.predictions,
            "experimental_evidence": self.experimental_evidence,
            "compatibility_score": self.compatibility_score,
            "scientific_value": self.scientific_value,
            "validated": self.validated,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ElectricityTheory":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            category=ElectricityTheoryCategory(data["category"]),
            timestamp=data["timestamp"],
            equations=data.get("equations", []),
            predictions=data.get("predictions", []),
            experimental_evidence=data.get("experimental_evidence", []),
            compatibility_score=data.get("compatibility_score", 0.0),
            scientific_value=data.get("scientific_value", 0.0),
            validated=data.get("validated", False),
        )


@dataclass
class ResearchRecord:
    """Запись об исследовании."""
    cycle: int
    topic: str
    source: str                     # "web", "project", "interaction", "self"
    findings: list[str] = field(default_factory=list)
    knowledge_gained: float = 0.0   # XP получено
    domain: KnowledgeDomain = KnowledgeDomain.ATMOSPHERIC_ELECTRICITY

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle": self.cycle,
            "topic": self.topic,
            "source": self.source,
            "findings": self.findings,
            "knowledge_gained": self.knowledge_gained,
            "domain": self.domain.value,
        }


# =====================================================================
#  ВЫЧИСЛЕНИЯ
# =====================================================================


@dataclass
class Calculation:
    """Электрическое вычисление."""
    id: str
    calculation_type: CalculationType
    timestamp: str
    input_params: dict[str, float] = field(default_factory=dict)
    result: float = 0.0
    units: str = ""
    precision: int = 6
    confidence: float = 0.0
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "calculation_type": self.calculation_type.value,
            "timestamp": self.timestamp,
            "input_params": self.input_params,
            "result": round(self.result, self.precision),
            "units": self.units,
            "precision": self.precision,
            "confidence": self.confidence,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Calculation":
        return cls(
            id=data["id"],
            calculation_type=CalculationType(data["calculation_type"]),
            timestamp=data["timestamp"],
            input_params=data.get("input_params", {}),
            result=data.get("result", 0.0),
            units=data.get("units", ""),
            precision=data.get("precision", 6),
            confidence=data.get("confidence", 0.0),
            notes=data.get("notes", ""),
        )


# =====================================================================
#  МОЛНИИ
# =====================================================================


@dataclass
class LightningStrike:
    """Данные о молнии."""
    id: str
    timestamp: str
    energy_joules: float = 0.0
    peak_current_amps: float = 0.0
    voltage: float = 0.0
    duration_seconds: float = 0.0
    altitude_meters: float = 0.0
    temperature_kelvin: float = 0.0
    charge_moved_coulombs: float = 0.0
    strike_type: str = "cloud_to_ground"  # cloud_to_ground, intra_cloud, etc
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "energy_joules": self.energy_joules,
            "peak_current_amps": self.peak_current_amps,
            "voltage": self.voltage,
            "duration_seconds": self.duration_seconds,
            "altitude_meters": self.altitude_meters,
            "temperature_kelvin": self.temperature_kelvin,
            "charge_moved_coulombs": self.charge_moved_coulombs,
            "strike_type": self.strike_type,
            "notes": self.notes,
        }


# =====================================================================
#  УРОВЕНЬ ЗНАНИЙ
# =====================================================================


@dataclass
class KnowledgeLevel:
    """Уровень знаний Фуюки."""
    level: int = 1
    xp: int = 0
    domain_xp: dict[str, int] = field(default_factory=dict)
    domains_studied: list[str] = field(default_factory=list)
    theories_count: int = 0
    calculations_count: int = 0
    papers_studied: int = 0
    web_searches: int = 0
    interactions_count: int = 0
    reports_written: int = 0
    character_traits_strengthened: int = 0

    # Карта уровней
    XP_PER_LEVEL = [
        0, 100, 300, 600, 1000, 1500, 2200, 3000, 4000, 5500,
        7000, 9000, 11000, 13500, 16500, 20000, 24000, 28500, 34000, 40000,
    ]

    def add_xp(self, amount: int, domain: KnowledgeDomain = KnowledgeDomain.ATMOSPHERIC_ELECTRICITY) -> bool:
        """Добавить опыт, вернуть True если уровень повышен."""
        old_level = self.level
        self.xp += amount
        domain_key = domain.value
        self.domain_xp[domain_key] = self.domain_xp.get(domain_key, 0) + amount

        # Проверяем повышение уровня
        threshold_idx = min(old_level, len(self.XP_PER_LEVEL) - 1)
        next_threshold = self.XP_PER_LEVEL[threshold_idx]

        if self.xp >= next_threshold and self.level < len(self.XP_PER_LEVEL):
            self.level += 1
            return True  # Уровень повышен!

        return False  # Уровень не повышен

    def get_level_name(self) -> str:
        """Получить имя текущего уровня."""
        level_names = [
            "Новичок", "Ученик", "Студент", "Исследователь", "Младший научный сотрудник",
            "Научный сотрудник", "Старший научный сотрудник", "Кандидат наук", "Доцент", "Профессор",
            "Ведущий исследователь", "Заведующий лабораторией", "Доктор наук", "Профессор мирового уровня",
            "Легенда физики", "Гений", "Мастер электричества", "Повелитель молний",
            "Хранитель атмосферы", "Бог электричества",
        ]
        idx = min(self.level - 1, len(level_names) - 1)
        return level_names[idx]

    def progress_to_next_level(self) -> float:
        """Прогресс до следующего уровня (0-100%)."""
        if self.level >= len(self.XP_PER_LEVEL):
            return 100.0
        current_threshold = self.XP_PER_LEVEL[self.level - 1]
        next_threshold = self.XP_PER_LEVEL[self.level]
        progress = (self.xp - current_threshold) / (next_threshold - current_threshold)
        return min(100.0, max(0.0, progress * 100))

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "level_name": self.get_level_name(),
            "xp": self.xp,
            "xp_to_next": self.XP_PER_LEVEL[min(self.level, len(self.XP_PER_LEVEL) - 1)] - self.xp,
            "progress_to_next": round(self.progress_to_next_level(), 1),
            "domain_xp": self.domain_xp,
            "domains_studied": self.domains_studied,
            "theories_count": self.theories_count,
            "calculations_count": self.calculations_count,
            "papers_studied": self.papers_studied,
            "web_searches": self.web_searches,
            "interactions_count": self.interactions_count,
            "reports_written": self.reports_written,
            "character_traits_strengthened": self.character_traits_strengthened,
        }
