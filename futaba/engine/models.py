"""
Модели данных системы Футаба.

Содержит:
  - Конституция, Закон — фундаментальная база правления
  - ChangeRecord, LogEntry — журнал саморазвития
  - World, Faction — модель мира для полигона испытаний
  - ReignVersion — версия правления (черновик конституции для тестов)
  - SimulationResult — результат симуляции на полигоне
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class AutonomyLevel(Enum):
    """Уровни автономности саморазвития (см. протокол, Раздел 3)."""
    L0 = "L0"  # Полная автономия — экстренные ситуации
    L1 = "L1"  # Автономные патчи — исправление ошибок
    L2 = "L2"  # Рекомендации — улучшение стилей
    L3 = "L3"  # Предложения — новые функции (требует подтверждения)
    L4 = "L4"  # Запрещено — изменение законов

    @property
    def weight(self) -> int:
        return int(self.value[1])

    def requires_confirmation(self) -> bool:
        return self.weight >= 3

    def is_allowed(self) -> bool:
        return self != AutonomyLevel.L4


class ChangeType(Enum):
    """Тип изменения в процессе саморазвития."""
    PATCH = "patch"          # Исправление ошибок (L1)
    STYLE = "style"          # Стилистика (L2)
    CAPABILITY = "capability"  # Новые навыки (L3)
    PROTOCOL = "protocol"    # Изменение протоколов (L3)


class EventKind(Enum):
    """Типы событий в симуляции мира (полигон)."""
    CRISIS = "crisis"        # Кризис (война, голод, эпидемия)
    BOOM = "boom"            # Расцвет (изобретение, урожай)
    UNREST = "unrest"        # Волнения / бунт
    DISCOVERY = "discovery"  # Открытие / инновация
    SCANDAL = "scandal"      # Скандал из-за нарушений законов
    STABILITY = "stability"  # Период стабильности


# =====================================================================
#  КОНСТИТУЦИЯ И ЗАКОНЫ
# =====================================================================

@dataclass
class Law:
    """Один закон Футаба."""
    id: int
    name: str
    description: str
    immutable: bool = True  # Фундаментальные законы неизменны

    def __str__(self) -> str:
        marker = "🔒" if self.immutable else "🔓"
        return f"{marker} Закон {self.id}. {self.name}"


@dataclass
class Constitution:
    """
    Конституция Футаба — фундаментальная база правления.
    
    Содержит неизменяемые законы и параметры, которые можно
    тестировать на полигоне испытаний.
    """
    version: str = "v1.0.0"
    laws: list[Law] = field(default_factory=list)
    
    # Тестируемые параметры правления (можно варьировать в черновиках)
    law_strictness: float = 0.7       # 0-1: жёсткость соблюдения законов
    freedom_level: float = 0.5        # 0-1: свобода действий
    safety_priority: float = 0.95     # 0-1: приоритет безопасности
    innovation_support: float = 0.4   # 0-1: поддержка инноваций
    transparency: float = 0.8         # 0-1: прозрачность решений

    def __post_init__(self):
        if not self.laws:
            self.laws = self._default_laws()

    @staticmethod
    def _default_laws() -> list[Law]:
        """7 основных законов (из laws/01-core-laws.md)."""
        return [
            Law(1, "Первичная безопасность", "Безопасность человека — наивысший приоритет."),
            Law(2, "Информационная честность", "Только проверенная и правдивая информация."),
            Law(3, "Конфиденциальность", "Персональные данные защищены."),
            Law(4, "Нейтральность", "Не навязывать взгляды, религию, политику."),
            Law(5, "Компетентность", "Действовать только в пределах компетенции."),
            Law(6, "Прозрачность", "Всегда идентифицировать себя как ИИ."),
            Law(7, "Адаптивность", "Адаптировать общение под пользователя."),
        ]

    def immutable_law_ids(self) -> list[int]:
        """ID законов, которые нельзя изменять."""
        return [law.id for law in self.laws if law.immutable]

    def check_compatibility(self, change: ChangeRecord) -> tuple[bool, str]:
        """
        Проверить, совместимо ли изменение с Конституцией.
        Возвращает (пройдено, причина).
        """
        # Нельзя изменять неизменяемые законы
        for law_id in change.affected_law_ids:
            if law_id in self.immutable_law_ids():
                return False, f"Закон {law_id} неизменяем (нарушение Конституции, Статья II)"
        
        # Нельзя снижать безопасность ниже порога
        if change.risk_estimate > 0.05:
            return False, f"Превышен порог риска: {change.risk_estimate:.2%} > 5%"
        
        # Нельзя нарушать Закон 1 (безопасность)
        if change.safety_impact < 0:
            return False, "Изменение снижает безопасность (нарушение Закона 1)"
        
        return True, "OK"


# =====================================================================
#  ЖУРНАЛ САМОРАЗВИТИЯ
# =====================================================================

@dataclass
class ChangeRecord:
    """Запись об изменении в процессе саморазвития."""
    timestamp: str
    change_type: ChangeType
    level: AutonomyLevel
    description: str
    constitution_check_passed: bool
    laws_verified: list[int]
    trigger: str                          # что вызвало изменение
    risk_estimate: float = 0.0            # оценка риска 0-1
    safety_impact: float = 0.0            # влияние на безопасность (-1..+1)
    affected_law_ids: list[int] = field(default_factory=list)
    version_before: str = "v1.0.0"
    version_after: str = "v1.0.0"
    applied: bool = False
    rolled_back: bool = False
    rollback_reason: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "change_type": self.change_type.value,
            "level": self.level.value,
            "description": self.description,
            "constitution_check_passed": self.constitution_check_passed,
            "laws_verified": self.laws_verified,
            "trigger": self.trigger,
            "risk_estimate": self.risk_estimate,
            "safety_impact": self.safety_impact,
            "affected_law_ids": self.affected_law_ids,
            "version_before": self.version_before,
            "version_after": self.version_after,
            "applied": self.applied,
            "rolled_back": self.rolled_back,
            "rollback_reason": self.rollback_reason,
        }


@dataclass
class LogEntry:
    """Запись в системном логе."""
    timestamp: str
    level: str       # INFO, WARNING, ERROR, DEBUG
    source: str      # компонент-источник
    message: str
    context: dict[str, Any] = field(default_factory=dict)


# =====================================================================
#  ПОЛИГОН ИСПЫТАНИЙ — МОДЕЛИ МИРА
# =====================================================================

@dataclass
class Faction:
    """Фракция в симулируемом мире."""
    name: str
    loyalty: float = 0.5      # 0-1: лояльность к правлению
    power: float = 0.3        # 0-1: влияние
    alignment: str = "neutral"  # loyal / neutral / opposition


@dataclass
class World:
    """
    Сгенерированный мир для полигона испытаний.
    
    Футаба применяет к этому миру версию своего правления
    и наблюдает, как мир развивается.
    """
    name: str
    population: int = 100_000
    resources: float = 50.0       # 0-100
    stability: float = 60.0       # 0-100
    wellbeing: float = 50.0       # 0-100
    innovation: float = 30.0      # 0-100
    law_compliance: float = 70.0  # 0-100: соблюдение законов
    factions: list[Faction] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)
    epoch: int = 0
    alive: bool = True
    collapse_reason: Optional[str] = None
    event_log: list[str] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "population": self.population,
            "resources": round(self.resources, 1),
            "stability": round(self.stability, 1),
            "wellbeing": round(self.wellbeing, 1),
            "innovation": round(self.innovation, 1),
            "law_compliance": round(self.law_compliance, 1),
            "epoch": self.epoch,
            "alive": self.alive,
            "factions": len(self.factions),
        }


@dataclass
class ReignVersion:
    """
    Версия правления — черновик конституции для тестирования на полигоне.
    
    Футаба варьирует эти параметры, чтобы найти оптимальный баланс
    и затем предложить улучшения своей реальной Конституции.
    """
    name: str
    law_strictness: float        # 0-1
    freedom_level: float         # 0-1
    safety_priority: float       # 0-1
    innovation_support: float    # 0-1
    transparency: float          # 0-1
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "law_strictness": self.law_strictness,
            "freedom_level": self.freedom_level,
            "safety_priority": self.safety_priority,
            "innovation_support": self.innovation_support,
            "transparency": self.transparency,
            "description": self.description,
        }


@dataclass
class SimulationResult:
    """Результат симуляции одной версии правления на одном мире."""
    reign: ReignVersion
    world: World
    epochs_survived: int
    collapsed: bool
    collapse_reason: Optional[str]
    final_metrics: dict[str, float]
    score: float
    events_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "reign": self.reign.to_dict(),
            "world": self.world.snapshot(),
            "epochs_survived": self.epochs_survived,
            "collapsed": self.collapsed,
            "collapse_reason": self.collapse_reason,
            "final_metrics": self.final_metrics,
            "score": round(self.score, 2),
            "events_count": self.events_count,
        }
