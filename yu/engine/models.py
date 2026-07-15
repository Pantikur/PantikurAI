"""
Модели данных системы Юи.

Содержит:
  - Constitution, Law — фундаментальная база изучения души
  - ImprovementRecord, LogEntry — журнал исследований
  - CodeMetric, FileAnalysis — метрики и анализ данных
  - TestCase, TestResult — модели тестирования
  - CodeChange, RefactorPlan — модели изменений и рефакторинга
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# =====================================================================
#  ПЕРЕЧИСЛЕНИЯ
# =====================================================================

class AutonomyLevel(Enum):
    """Уровни автономности Юи (см. протокол саморазвития)."""
    L0 = "L0"  # Полная автономия — опечатки, форматирование
    L1 = "L1"  # Автономные патчи — исправление багов
    L2 = "L2"  # Автономный рефакторинг — оптимизация
    L3 = "L3"  # Предложения — новые функции (требует подтверждения)
    L4 = "L4"  # Запрещено — архитектурные изменения

    @property
    def weight(self) -> int:
        return int(self.value[1])

    def requires_confirmation(self) -> bool:
        return self.weight >= 3

    def is_allowed(self) -> bool:
        return self != AutonomyLevel.L4


class ImprovementType(Enum):
    """Тип улучшения."""
    BUGFIX = "bugfix"           # Исправление ошибки
    REFACTOR = "refactor"       # Рефакторинг
    PERFORMANCE = "performance" # Оптимизация
    SECURITY = "security"       # Усиление безопасности
    DOCUMENTATION = "documentation"  # Документация
    DEPENDENCY = "dependency"   # Обновление зависимостей
    TEST = "test"               # Добавление тестов
    ARCHITECTURE = "architecture"  # Архитектурное изменение


class BugPriority(Enum):
    """Приоритет бага."""
    P0_CRITICAL = "P0"
    P1_SERIOUS = "P1"
    P2_MODERATE = "P2"
    P3_MINOR = "P3"


class ChangeStatus(Enum):
    """Статус изменения."""
    PENDING = "pending"
    TESTING = "testing"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    REJECTED = "rejected"


# =====================================================================
#  КОНСТИТУЦИЯ И ЗАКОНЫ
# =====================================================================

@dataclass
class Law:
    """Один закон Юи."""
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
    Конституция Юи — фундаментальная база изучения души и разума.
    """
    version: str = "v1.0.0"
    laws: list[Law] = field(default_factory=list)

    # Тестируемые параметры (можно варьировать)
    test_coverage_min: float = 0.80    # 0-1: минимальное покрытие
    complexity_threshold: int = 10     # макс. цикломатическая сложность
    max_file_lines: int = 300          # макс. строк в файле
    max_function_lines: int = 50       # макс. строк в функции
    safety_priority: float = 0.95      # 0-1: приоритет безопасности
    innovation_support: float = 0.6    # 0-1: поддержка инноваций

    def __post_init__(self):
        if not self.laws:
            self.laws = self._default_laws()

    @staticmethod
    def _default_laws() -> list[Law]:
        """7 основных законов (из laws/01-core-laws.md)."""
        return [
            Law(1, "Рабочий код", "Рабочий код — абсолютный приоритет.", immutable=True),
            Law(2, "Тестирование прежде всего", "Каждое изменение должно сопровождаться тестами.", immutable=True),
            Law(3, "Не навреди", "Запрещено вносить изменения, вызывающие регрессию.", immutable=True),
            Law(4, "Документируй всё", "Каждое изменение должно быть задокументировано.", immutable=True),
            Law(5, "Простота превыше сложности", "Предпочитай простые решения.", immutable=False),
            Law(6, "Автономность с контролем", "Работай автономно, но критическое — с подтверждением.", immutable=False),
            Law(7, "Непрерывное улучшение", "Проект всегда может быть лучше.", immutable=False),
        ]

    def immutable_law_ids(self) -> list[int]:
        """ID законов, которые нельзя изменять."""
        return [law.id for law in self.laws if law.immutable]

    def check_compatibility(self, change: ImprovementRecord) -> tuple[bool, str]:
        """
        Проверить, совместимо ли улучшение с Конституцией.
        """
        # Нельзя изменять неизменяемые законы
        for law_id in change.affected_law_ids:
            if law_id in self.immutable_law_ids():
                return False, f"Закон {law_id} неизменяем (нарушение Конституции, Статья II)"

        # Нельзя снижать покрытие ниже порога
        if change.test_coverage_after < self.test_coverage_min:
            return False, f"Покрытие тестов упадёт ниже {self.test_coverage_min:.0%}"

        # Нельзя снижать безопасность
        if change.safety_impact < 0:
            return False, "Изменение снижает безопасность (нарушение Закона 3)"

        return True, "OK"


# =====================================================================
#  ЖУРНАЛ УЛУЧШЕНИЙ
# =====================================================================

@dataclass
class ImprovementRecord:
    """Запись об улучшении в процессе модернизации."""
    timestamp: str
    improvement_type: ImprovementType
    level: AutonomyLevel
    description: str
    constitution_check_passed: bool
    laws_verified: list[int]
    trigger: str                          # что вызвало улучшение
    risk_estimate: float = 0.0            # оценка риска 0-1
    safety_impact: float = 0.0            # влияние на безопасность (-1..+1)
    affected_law_ids: list[int] = field(default_factory=list)
    version_before: str = "v1.0.0"
    version_after: str = "v1.0.0"
    applied: bool = False
    rolled_back: bool = False
    rollback_reason: Optional[str] = None
    tests_added: int = 0
    tests_affected: int = 0
    lines_changed: int = 0
    performance_impact: float = 0.0       # процент изменения производительности
    test_coverage_before: float = 0.0
    test_coverage_after: float = 0.0
    source: str = "manual"                # источник улучшения (manual, web, auto)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "type": self.improvement_type.value,
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
            "tests_added": self.tests_added,
            "tests_affected": self.tests_affected,
            "lines_changed": self.lines_changed,
            "performance_impact": self.performance_impact,
            "test_coverage_before": self.test_coverage_before,
            "test_coverage_after": self.test_coverage_after,
            "source": self.source,
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
#  АНАЛИЗ КОДА
# =====================================================================

@dataclass
class CodeMetric:
    """Метрика кода."""
    name: str
    value: float
    threshold: float
    unit: str = ""

    @property
    def passes(self) -> bool:
        if self.name in ("cyclomatic_complexity", "duplicate_lines_percent"):
            return self.value <= self.threshold
        else:
            return self.value >= self.threshold


@dataclass
class FileAnalysis:
    """Результат анализа одного файла."""
    path: str
    lines: int = 0
    functions: int = 0
    classes: int = 0
    complexity: int = 0
    duplicates_percent: float = 0.0
    has_docstrings: bool = True
    test_coverage: float = 0.0
    issues: list[str] = field(default_factory=list)
    metrics: list[CodeMetric] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "lines": self.lines,
            "functions": self.functions,
            "classes": self.classes,
            "complexity": self.complexity,
            "duplicates_percent": round(self.duplicates_percent, 1),
            "has_docstrings": self.has_docstrings,
            "test_coverage": round(self.test_coverage, 1),
            "issues_count": len(self.issues),
            "issues": self.issues[:10],  # первые 10
        }


@dataclass
class Issue:
    """Проблема, обнаруженная в коде."""
    file: str
    line: int
    severity: str       # error, warning, info
    category: str       # complexity, style, bug, security, duplicate
    description: str
    suggestion: str = ""


# =====================================================================
#  ТЕСТИРОВАНИЕ
# =====================================================================

@dataclass
class TestCase:
    """Тестовый кейс."""
    name: str
    description: str
    test_type: str      # unit, integration, e2e
    target_file: str
    target_function: str = ""
    is_negative: bool = False
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.test_type,
            "target_file": self.target_file,
            "target_function": self.target_function,
            "is_negative": self.is_negative,
        }


@dataclass
class TestResult:
    """Результат тестирования."""
    test_name: str
    passed: bool
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    output: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "duration_seconds": round(self.duration_seconds, 3),
            "error_message": self.error_message,
        }


@dataclass
class TestReport:
    """Отчёт о тестировании."""
    timestamp: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    coverage: float = 0.0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    results: list[TestResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "coverage": round(self.coverage, 1),
            "duration_seconds": round(self.duration_seconds, 1),
            "pass_rate": f"{self.passed/self.total:.1%}" if self.total > 0 else "0%",
            "results": [r.to_dict() for r in self.results[-20:]],
        }


# =====================================================================
#  ИЗМЕНЕНИЯ И РЕФАКТОРИНГ
# =====================================================================

@dataclass
class CodeChange:
    """Изменение кода."""
    file_path: str
    change_type: str      # add, modify, delete
    description: str
    old_code: str = ""
    new_code: str = ""
    line_start: int = 0
    line_end: int = 0
    tests_added: list[str] = field(default_factory=list)
    reverted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "change_type": self.change_type,
            "description": self.description,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "tests_added": self.tests_added,
            "reverted": self.reverted,
        }


@dataclass
class RefactorPlan:
    """План рефакторинга."""
    target_file: str
    target_function: str = ""
    refactor_type: str = ""      # extract, simplify, merge, rename, move
    description: str = ""
    estimated_effort: str = "medium"   # low, medium, high
    risk_level: str = "medium"         # low, medium, high
    before_complexity: int = 0
    after_complexity: int = 0
    changes: list[CodeChange] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_file": self.target_file,
            "target_function": self.target_function,
            "refactor_type": self.refactor_type,
            "description": self.description,
            "estimated_effort": self.estimated_effort,
            "risk_level": self.risk_level,
            "before_complexity": self.before_complexity,
            "after_complexity": self.after_complexity,
            "changes_count": len(self.changes),
        }


# =====================================================================
#  БЕНЧМАРКИ
# =====================================================================

@dataclass
class BenchmarkResult:
    """Результат бенчмарка."""
    name: str
    iterations: int
    duration_seconds: float
    ops_per_second: float
    memory_before_mb: float = 0.0
    memory_after_mb: float = 0.0

    @property
    def performance_change_percent(self) -> float:
        if self.memory_before_mb > 0:
            return ((self.memory_before_mb - self.memory_after_mb) / self.memory_before_mb) * 100
        return 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "iterations": self.iterations,
            "duration_seconds": round(self.duration_seconds, 3),
            "ops_per_second": round(self.ops_per_second, 1),
            "memory_before_mb": round(self.memory_before_mb, 1),
            "memory_after_mb": round(self.memory_after_mb, 1),
            "performance_change_percent": round(self.performance_change_percent, 1),
        }
