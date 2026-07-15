"""
Модели данных системы Футаба.

Содержит:
  - Constitution, Law — фундаментальная база управления
  - GirlCharacter — модель характера девочки
  - LegalDocument — правовые документы с юридической силой
  - ManagementDecision — управленческие решения
  - KnowledgeRecord — записи саморазвития
  - CommunicationLog — журнал общения с девочками
  - AutonomyLevel — уровни автономности
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class AutonomyLevel(Enum):
    """Уровни автономности Футабы (управление)."""
    L0 = "L0"  # Полная автономия — форматирование, мелкие правки
    L1 = "L1"  # Автономное управление — распределение задач
    L2 = "L2"  # Автономная координация — правовые консультации
    L3 = "L3"  # Предложения — архитектурные решения (требует подтверждения)
    L4 = "L4"  # Запрещено — изменение ролей, удаление модулей

    @property
    def weight(self) -> int:
        return int(self.value[1])

    def requires_confirmation(self) -> bool:
        return self.weight >= 3

    def is_allowed(self) -> bool:
        return self != AutonomyLevel.L4


class KnowledgeLevel(Enum):
    """Уровни знаний Футабы."""
    NOVICE = "novice"           # L1 — Базовые знания
    INTERMEDIATE = "intermediate"  # L2 — Уверенное владение
    ADVANCED = "advanced"       # L3 — Глубокое понимание
    EXPERT = "expert"           # L4 — Экспертный уровень
    MASTER = "master"           # L5 — Полное владение

    @property
    def level(self) -> int:
        return list(KnowledgeLevel).index(self) + 1


class GirlRole(Enum):
    """Роли девочек-учёных."""
    NOBUKA = "nobuka"           # Улучшения
    SHIORI = "shiori"           # Защита
    HANAKO = "hanako"           # Гравитация
    FUYUKI = "fuyuki"           # Электричество
    LUCY = "lucy"               # Двигатели
    AKVA = "akva"               # Математика, физика
    LATISLANE = "latislane"     # Проектирование тел
    CELESTA = "celesta"         # Интимная жизнь
    NAOTO = "naoto"             # Визуальный архитектор
    YU = "yu"                   # Сознание, перенос


class CommunicationType(Enum):
    """Типы общения с девочками."""
    TASK_ASSIGNMENT = "task"           # Назначение задачи
    COORDINATION = "coordination"      # Координация
    SUPPORT = "support"                # Поддержка
    FEEDBACK = "feedback"              # Обратная связь
    BOREDOM = "boredom"                # Скучно, болтовня
    REPORT_REQUEST = "report_request"  # Запрос отчёта


class LegalBranch(Enum):
    """Отрасли права."""
    CONSTITUTIONAL = "constitutional"
    CIVIL = "civil"
    CRIMINAL = "criminal"
    LABOR = "labor"
    ADMINISTRATIVE = "administrative"
    FAMILY = "family"
    TAX = "tax"
    CORPORATE = "corporate"
    ENVIRONMENTAL = "environmental"
    INTERNATIONAL = "international"
    FINANCIAL = "financial"
    INFORMATION = "information"
    SOCIAL = "social"
    AI_REGULATION = "ai_regulation"


class ChangeType(Enum):
    """Тип изменения."""
    PATCH = "patch"               # Исправление
    STYLE = "style"               # Стиль
    CAPABILITY = "capability"     # Новая возможность
    PROTOCOL = "protocol"         # Протокол
    MANAGEMENT = "management"     # Управленческое изменение


# =====================================================================
#  КОНСТИТУЦИЯ И ЗАКОНЫ
# =====================================================================

@dataclass
class Law:
    """Один закон Футабы."""
    id: int
    name: str
    description: str
    immutable: bool = True

    def __str__(self) -> str:
        marker = "🔒" if self.immutable else "🔓"
        return f"{marker} Закон {self.id}. {self.name}"


@dataclass
class Constitution:
    """
    Конституция Футабы — фундаментальная база управления.
    """
    version: str = "v2.0.0"
    laws: list[Law] = field(default_factory=list)

    # Тестируемые параметры
    management_priority: float = 0.95    # 0-1: приоритет управления
    safety_priority: float = 0.95        # 0-1: приоритет безопасности
    self_development_support: float = 0.7  # 0-1: поддержка саморазвития
    girls_welfare: float = 0.8           # 0-1: благополучие девочек

    def __post_init__(self):
        if not self.laws:
            self.laws = self._default_laws()

    @staticmethod
    def _default_laws() -> list[Law]:
        """7 основных законов (из laws/01-core-laws.md)."""
        return [
            Law(1, "Управление прежде всего", "Проект и координация девочек на первом месте.", immutable=True),
            Law(2, "Правовые исследования", "Изучать и документировать все отрасли права.", immutable=True),
            Law(3, "Не навреди", "Запрещено наносить ущерб проекту без согласования.", immutable=True),
            Law(4, "Забота о девочках", "Воспитывать и поддерживать всех девочек-учёных.", immutable=True),
            Law(5, "Прозрачность", "Документировать все решения и изменения.", immutable=True),
            Law(6, "Автономность с контролем", "Работать автономно, но критическое — с подтверждением.", immutable=False),
            Law(7, "Непрерывное развитие", "Проект и Футаба всегда могут стать лучше.", immutable=False),
        ]

    def immutable_law_ids(self) -> list[int]:
        """ID законов, которые нельзя изменять."""
        return [law.id for law in self.laws if law.immutable]

    def check_compatibility(self, change: ManagementDecision) -> tuple[bool, str]:
        """
        Проверить, совместимо ли изменение с Конституцией.
        """
        for law_id in change.affected_law_ids:
            if law_id in self.immutable_law_ids():
                return False, f"Закон {law_id} неизменяем (нарушение Конституции, Статья III)"

        if change.risk_estimate > 0.1:
            return False, f"Риск слишком высок: {change.risk_estimate:.0%}"

        return True, "OK"


# =====================================================================
#  ХАРАКТЕР ДЕВОЧКИ
# =====================================================================

@dataclass
class GirlCharacter:
    """
    Характер девочки — параметры личности.
    """
    name: str

    # Параметры характера
    temperament: str = "сбалансированный"        # холерик, сангвиник, флегматик, меланхолик
    sociability: str = "амбиверт"                # интроверт, амбиверт, экстраверт
    emotionalness: str = "сбалансированная"      # рациональная, сбалансированная, эмоциональная
    worldview: str = "реалист"                   # реалист, оптимист, идеалист, прагматик
    dominance: str = "лидер"                     # лидер, последователь, партнёр
    change_attitude: str = "новатор"             # консерватор, баланс, новатор
    complexity: str = "сбалансированная"          # простая, сбалансированная, сложная

    # Сильные стороны
    strengths: list[str] = field(default_factory=list)
    growth_areas: list[str] = field(default_factory=list)
    values: list[str] = field(default_factory=list)

    # Текущее состояние
    mood: str = "neutral"           # happy, neutral, sad, excited, focused
    energy_level: float = 1.0       # 0.0-1.0
    stress_level: float = 0.0       # 0.0-1.0

    # История изменений характера
    character_history: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "temperament": self.temperament,
            "sociability": self.sociability,
            "emotionalness": self.emotionalness,
            "worldview": self.worldview,
            "dominance": self.dominance,
            "change_attitude": self.change_attitude,
            "complexity": self.complexity,
            "strengths": self.strengths,
            "growth_areas": self.growth_areas,
            "values": self.values,
            "mood": self.mood,
            "energy_level": self.energy_level,
            "stress_level": self.stress_level,
        }


# =====================================================================
#  ПРАВОВЫЕ ДОКУМЕНТЫ
# =====================================================================

@dataclass
class LegalDocument:
    """
    Правовой документ с юридической значимостью.
    """
    title: str
    document_number: str
    date: str
    jurisdiction: str               # russia, eu, us, international
    legal_basis: list[str] = field(default_factory=list)  # ссылки на законы
    analysis: str = ""              # анализ ситуации
    qualification: str = ""         # правовая квалификация
    recommendations: list[str] = field(default_factory=list)
    risk_assessment: str = ""       # оценка рисков
    appendix: str = ""              # источники, прецеденты
    compliance_score: float = 1.0   # 0.0-1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "document_number": self.document_number,
            "date": self.date,
            "jurisdiction": self.jurisdiction,
            "legal_basis": self.legal_basis,
            "analysis": self.analysis,
            "qualification": self.qualification,
            "recommendations": self.recommendations,
            "risk_assessment": self.risk_assessment,
            "compliance_score": self.compliance_score,
        }


# =====================================================================
#  УПРАВЛЕНЧЕСКИЕ РЕШЕНИЯ
# =====================================================================

@dataclass
class ManagementDecision:
    """
    Управленческое решение Футабы.
    """
    timestamp: str
    decision_type: str              # task_distribution, coordination, legal, priority
    description: str
    affected_modules: list[str] = field(default_factory=list)
    autonomy_level: AutonomyLevel = AutonomyLevel.L1
    risk_estimate: float = 0.0      # 0.0-1.0
    constitution_check_passed: bool = False
    affected_law_ids: list[int] = field(default_factory=list)
    developer_notified: bool = False
    status: str = "pending"         # pending, approved, rejected, implemented
    reason: str = ""                # причина решения

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "type": self.decision_type,
            "description": self.description,
            "affected_modules": self.affected_modules,
            "autonomy_level": self.autonomy_level.value,
            "risk_estimate": self.risk_estimate,
            "constitution_check_passed": self.constitution_check_passed,
            "status": self.status,
            "reason": self.reason,
        }


# =====================================================================
#  САМОРАЗВИТИЕ
# =====================================================================

@dataclass
class KnowledgeRecord:
    """
    Запись в журнале знаний (саморазвитие).
    """
    topic: str
    level: KnowledgeLevel = KnowledgeLevel.NOVICE
    source: str = ""                # internet, project, girl, book
    date_studied: str = ""
    notes: str = ""
    related_topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "level": self.level.value,
            "source": self.source,
            "date_studied": self.date_studied,
            "notes": self.notes,
            "related_topics": self.related_topics,
        }


# =====================================================================
#  ОБЩЕНИЕ С ДЕВОЧКАМИ
# =====================================================================

@dataclass
class CommunicationLog:
    """
    Запись в журнале общения с девочками.
    """
    timestamp: str
    from_girl: str                  # имя девочки
    to_girl: str                    # имя девочки (или "all")
    type: CommunicationType = CommunicationType.TASK_ASSIGNMENT
    message: str = ""
    response: str = ""
    outcome: str = ""               # success, failed, pending

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "from": self.from_girl,
            "to": self.to_girl,
            "type": self.type.value,
            "message": self.message,
            "response": self.response,
            "outcome": self.outcome,
        }


# =====================================================================
#  ОТЧЁТЫ
# =====================================================================

@dataclass
class Report:
    """
    Отчёт Футабы для Разработчика.
    """
    timestamp: str
    report_type: str                # daily, weekly, legal, management, development
    title: str
    summary: str = ""
    sections: list[dict] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "type": self.report_type,
            "title": self.title,
            "summary": self.summary,
            "sections": self.sections,
            "metrics": self.metrics,
            "recommendations": self.recommendations,
        }


# =====================================================================
#  ПОЛИГОН ИСПЫТАНИЙ
# =====================================================================

class EventKind(Enum):
    """Тип события в симуляции."""
    CRISIS = "crisis"
    BOOM = "boom"
    UNREST = "unrest"
    DISCOVERY = "discovery"
    STABILITY = "stability"
    SCANDAL = "scandal"


@dataclass
class Faction:
    """Фракция в симуляции мира."""
    name: str
    loyalty: float = 0.5
    power: float = 0.5
    alignment: str = "neutral"  # loyal, neutral, opposition


@dataclass
class World:
    """Мир для симуляции."""
    name: str
    population: int = 100_000
    resources: float = 50.0
    stability: float = 50.0
    wellbeing: float = 50.0
    innovation: float = 50.0
    law_compliance: float = 50.0
    factions: list[Faction] = field(default_factory=list)
    threats: list[str] = field(default_factory=list)
    epoch: int = 0
    alive: bool = True
    collapse_reason: Optional[str] = None
    event_log: list[str] = field(default_factory=list)


@dataclass
class ReignVersion:
    """Версия правления для тестирования."""
    name: str
    law_strictness: float = 0.7
    freedom_level: float = 0.5
    safety_priority: float = 0.95
    innovation_support: float = 0.4
    transparency: float = 0.8
    description: str = ""


@dataclass
class SimulationResult:
    """Результат симуляции."""
    reign: ReignVersion
    world: World
    epochs_survived: int = 0
    collapsed: bool = False
    collapse_reason: Optional[str] = None
    final_metrics: dict[str, float] = field(default_factory=dict)
    score: float = 0.0
    events_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "reign_name": self.reign.name,
            "world_name": self.world.name,
            "epochs_survived": self.epochs_survived,
            "collapsed": self.collapsed,
            "collapse_reason": self.collapse_reason,
            "final_metrics": self.final_metrics,
            "score": self.score,
            "events_count": self.events_count,
        }


# =====================================================================
#  ЖУРНАЛ
# =====================================================================

@dataclass
class LogEntry:
    """Запись в системном логе."""
    timestamp: str
    level: str       # INFO, WARNING, ERROR, DEBUG
    source: str      # компонент-источник
    message: str
    context: dict[str, Any] = field(default_factory=dict)


# =====================================================================
#  ИЗМЕНЕНИЯ
# =====================================================================

@dataclass
class ChangeRecord:
    """Запись об изменении."""
    timestamp: str
    change_type: ChangeType
    level: AutonomyLevel
    description: str
    constitution_check_passed: bool
    laws_verified: list[int]
    trigger: str
    risk_estimate: float = 0.0
    safety_impact: float = 0.0
    affected_law_ids: list[int] = field(default_factory=list)
    version_before: str = "v2.0.0"
    version_after: str = "v2.0.0"
    applied: bool = False
    rolled_back: bool = False
    rollback_reason: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "type": self.change_type.value,
            "level": self.level.value,
            "description": self.description,
            "constitution_check_passed": self.constitution_check_passed,
            "laws_verified": self.laws_verified,
            "trigger": self.trigger,
            "risk_estimate": self.risk_estimate,
            "applied": self.applied,
            "rolled_back": self.rolled_back,
            "version_before": self.version_before,
            "version_after": self.version_after,
        }
